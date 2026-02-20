# Copyright 2025 GARR.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import uuid
from typing import Annotated, Any

from orchestrator.db import db
from orchestrator.db.models import (
    InputStateTable,
    ProcessSubscriptionTable,
    ProcessTable,
    SubscriptionInstanceRelationTable,
    SubscriptionInstanceTable,
    SubscriptionTable,
)
from orchestrator.forms import FormPage
from orchestrator.targets import Target
from orchestrator.workflow import StepList, begin, done, step, workflow
from pydantic import Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr

# warning text
achtung = (
    "Please ensure that you have a backup of the database before proceeding. "
    "This is a last resort for cleaning up hung subscriptions. "
    "This task will *irreversibly* delete a subscription and all its blocks, values, "
    "relations and any processes tied to it from the database. "
    "THERE IS NO UNDO. "
    "No action will be performed on external devices and systems. Do it manually if needed. "
    "To proceed, replace this message by typing DELETE exactly."
)
Achtung = Annotated[
    str,
    Field(
        achtung,
        title="⚠️⚠️⚠️ ACHTUNG ⚠️⚠️⚠️",
        json_schema_extra={"format": "long"},
    ),
]


# initial form inputs
def initial_input_form_generator() -> FormGenerator:
    class InputForm(FormPage):
        achtung: Achtung
        subscription_id: UUIDstr = Field(
            ..., title="Subscription ID", description="UUID of the hung subscription"
        )

        @model_validator(mode="after")
        def check_confirm(self) -> "InputForm":
            if self.achtung != "DELETE":
                msg = "Read the ⚠️⚠️⚠️ ACHTUNG ⚠️⚠️⚠️ message!"
                raise ValueError(
                    msg
                )
            return self

    user_input = yield InputForm
    return user_input.dict()


@step("Check that no other instances depend on this subscription")
def check_dependencies(subscription_id: str) -> State:
    """
    Checks if a given subscription can be safely deleted by verifying two conditions:
    1. The subscription is not currently 'in sync'.
    2. No other subscription instances depend on any instances of this subscription.

    Args:
        subscription_id: The UUID string of the subscription to check.

    Returns:
        An empty dictionary (State) if no dependencies are found and the subscription
        is not in sync, indicating that deletion can proceed.

    Raises:
        ValueError:
            - If the subscription with the given ID is not found.
            - If the subscription is 'in sync' (should be terminated via a different workflow).
            - If other subscription instances are found to depend on instances of this subscription.
              The error message will detail which subscriptions depend on which instances.
    """
    session = db.session
    sub = session.get(SubscriptionTable, uuid.UUID(subscription_id))
    if not sub:
        raise ValueError(f"Subscription {subscription_id} not found")
    if sub.insync is True:
        raise ValueError(
            f"Subscription {subscription_id} is in sync, use terminate workflow instead."
        )

    instances_ids = [si.subscription_instance_id for si in sub.instances]
    # find any relations where another instance depends on these
    dependent_instance_relations = (
        session.query(SubscriptionInstanceRelationTable)
        .filter(SubscriptionInstanceRelationTable.depends_on_id.in_(instances_ids))
        .all()
    )

    dependent_subscriptions_ids = set()
    if dependent_instance_relations:
        for relation in dependent_instance_relations:
            dependent_instance_id = relation.in_use_by_id
            owner_sub_id = (
                session.query(SubscriptionInstanceTable)
                .filter_by(subscription_instance_id=dependent_instance_id)
                .one()
            ).subscription_id
            if (
                str(owner_sub_id) != subscription_id
                and str(owner_sub_id) not in dependent_subscriptions_ids
            ):
                dependent_subscriptions_ids.add(str(owner_sub_id))

    if dependent_subscriptions_ids:
        raise ValueError(
            "Cannot delete: found dependent subscriptions: "
            + ", ".join(dependent_subscriptions_ids)
        )

    return {
        "passed_checks": "The subscription is not currently 'in sync' and no other subscription instances depend on any instance of this subscription."
    }


@step("Delete subscription, its instances and any processes")
def delete_db_entries(subscription_id: str) -> State:
    """
    Deletes a subscription, its related instances, and any associated processes from the database.

    This function performs the following actions:
    1. Retrieves the subscription by its ID.
    2. Finds all process IDs (PIDs) linked to this subscription.
    3. If PIDs are found:
        a. Deletes corresponding entries from `InputStateTable`.
        b. Deletes corresponding entries from `ProcessTable`.
           (This is expected to cascade to `ProcessStepTable` and `ProcessSubscriptionTable`
            if `ON DELETE CASCADE` is configured for their foreign keys).
    4. Deletes the subscription itself (which should cascade to instances, values, and relations).
    5. Flushes the database session to apply changes. The commit is expected to be handled
       by the workflow engine.

    Args:
        subscription_id: The UUID string of the subscription to be deleted.

    Returns:
        A dictionary (State) summarizing the operations performed, including counts of
        deleted entries and status messages.
    """
    report: dict[str, Any] = {}
    session = db.session
    sub = session.get(SubscriptionTable, uuid.UUID(subscription_id))

    # find all process IDs tied to this subscription
    processes_subscriptions = (
        session.query(ProcessSubscriptionTable)
        .filter_by(subscription_id=sub.subscription_id)
        .all()
    )
    pids = [r.process_id for r in processes_subscriptions]
    report["count_related_processes"] = len(pids)

    if pids:
        # Delete related InputStateTable entries first.
        num_del = (
            session.query(InputStateTable)
            .filter(InputStateTable.process_id.in_(pids))
            .delete()
        )
        report["count_input_states_deleted"] = num_del

        # Then, delete the ProcessTable entries.
        # This should cascade to ProcessStepTable and ProcessSubscriptionTable
        # if their respective foreign keys have ON DELETE CASCADE.
        num_del = (
            session.query(ProcessTable)
            .filter(ProcessTable.process_id.in_(pids))
            .delete()
        )
        report["count_processes_deleted"] = num_del

    # delete the subscription (cascade → instances, values & relations)
    session.delete(sub)
    report["is_subscription_deleted"] = True

    # flush; commit is handled by the workflow engine
    session.flush()
    return report


@workflow(
    "Purge subscription and all its blocks, values, relations and any processes tied to it from the database",
    target=Target.SYSTEM,
    initial_input_form=initial_input_form_generator,
)
def purge_subscription_from_database() -> StepList:
    return begin >> check_dependencies >> delete_db_entries >> done
