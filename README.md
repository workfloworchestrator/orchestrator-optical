# Workflow Orchestrator (WFO) Optical Module

## Project Overview

The WFO Optical Module is a Python module that can be installed as a dependency for
[WFO](https://workfloworchestrator.org) users that want to integrate with their optical equipment. This project is
built on top of [`orchestrator-core`](https://github.com/workfloworchestrator/orchestrator-core).

## Installation

To use the models and services from this module, you will need to make some changes to your local implementation of the
WFO. Please follow the steps below to install the WFO Optical module, including some file edits:

1. `uv add orchestrator-optical`
2. Generate a database migration for this module in your local `migrations` setup via the orchestrator-core
   shell commands.
3. The module is currently a work in progress (ported from a GARR-specific implementation): the model files are still
   being finalized and are subject to change between releases. See the "Consumption model" section below for how to
   decouple your own products from those changes.

## Consumption model

The module ships **concrete product blocks** (e.g. `OpticalNodeBlock`, `OpticalFiberSpanBlock`), the matching
subscription product types, hardware abstraction layer `hal/` services, the **ready-to-use workflows of the shipped product types** (one
create/modify/terminate/validate per product) and the **parts of the workflows** (the FormPages of the shipped forms,
as page sequences, and the step lists). The module expects you to use the shipped concrete blocks as a **shared
interface** that you compose with your own model.

### Architecture

The module is strictly layered: `products/` (blocks and subscription models) → `hal/` (device-facing logic) →
`workflows/` (orchestration), with `services/` (device integrations) under `hal/`. **Blocks are the shared
contracts**: `hal/` depends only on blocks, never on subscription models — a subscription id may be an input
parameter, but it is resolved to a block, never to a model. Consequently nothing under `hal/` imports from
`workflows/`; the database queries both layers need live in the neutral `orchestrator/optical/db.py`. This keeps the
hardware layer usable, maintainable and evolvable independently of any workflow or consumer model.

There are two consumption paths:

### 1. Use the shipped product types and their workflows as-is

Keep the shipped subscription product types. The module ships one ready-to-use workflow per product type and
lifecycle target (create / modify / terminate / validate), as plain `@create_workflow` / `@modify_workflow` /
`@terminate_workflow` / `@validate_workflow`-decorated functions bound to the shipped subscription models. They are
only valid when you keep the shipped product types.

Register them with the standard orchestrator-core mechanism: one `LazyWorkflowInstance` line per workflow in your own
workflows package.

```python
# mywfo/workflows/__init__.py
from orchestrator.core.workflows import LazyWorkflowInstance

LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_flexils.create", "create_optical_node_nokia_flexils")
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_flexils.modify", "modify_optical_node_nokia_flexils")
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_flexils.terminate", "terminate_optical_node_nokia_flexils")
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_flexils.validate", "validate_optical_node_nokia_flexils")
```

Then persist the workflows to the database with the orchestrator-core CLI (`orchestrator db migrate-workflows`) and
bind them to your product types. If you keep the shipped workflow names, the display strings in
`orchestrator/optical/translations/en-GB.json` apply as-is; otherwise declare your own translations.

The full list of shipped workflows and their import paths:

| Workflow                              | Module                                                                                              |
|---------------------------------------|-----------------------------------------------------------------------------------------------------|
| `create_optical_node_nokia_flexils`   | `orchestrator.optical.workflows.optical_node.nokia_flexils.create`                                  |
| `modify_optical_node_nokia_flexils`   | `orchestrator.optical.workflows.optical_node.nokia_flexils.modify`                                  |
| `terminate_optical_node_nokia_flexils`| `orchestrator.optical.workflows.optical_node.nokia_flexils.terminate`                               |
| `validate_optical_node_nokia_flexils` | `orchestrator.optical.workflows.optical_node.nokia_flexils.validate`                                |
| `create_optical_node_nokia_groove_g30`| `orchestrator.optical.workflows.optical_node.nokia_groove_g30.create`                               |
| `modify_optical_node_nokia_groove_g30`| `orchestrator.optical.workflows.optical_node.nokia_groove_g30.modify`                               |
| `terminate_optical_node_nokia_groove_g30` | `orchestrator.optical.workflows.optical_node.nokia_groove_g30.terminate`                        |
| `validate_optical_node_nokia_groove_g30` | `orchestrator.optical.workflows.optical_node.nokia_groove_g30.validate`                         |
| `create_optical_node_nokia_gx_g42`    | `orchestrator.optical.workflows.optical_node.nokia_gx_g42.create`                                   |
| `modify_optical_node_nokia_gx_g42`    | `orchestrator.optical.workflows.optical_node.nokia_gx_g42.modify`                                   |
| `terminate_optical_node_nokia_gx_g42` | `orchestrator.optical.workflows.optical_node.nokia_gx_g42.terminate`                                |
| `validate_optical_node_nokia_gx_g42`  | `orchestrator.optical.workflows.optical_node.nokia_gx_g42.validate`                                 |
| `create_optical_coherent_pluggable`   | `orchestrator.optical.workflows.optical_coherent_pluggable.create`                                  |
| `modify_optical_coherent_pluggable`   | `orchestrator.optical.workflows.optical_coherent_pluggable.modify`                                  |
| `terminate_optical_coherent_pluggable`| `orchestrator.optical.workflows.optical_coherent_pluggable.terminate`                               |
| `validate_optical_coherent_pluggable` | `orchestrator.optical.workflows.optical_coherent_pluggable.validate`                                |
| `create_fiber_span`                   | `orchestrator.optical.workflows.optical_pipe.fiber_span.create`                                     |
| `modify_fiber_span`                   | `orchestrator.optical.workflows.optical_pipe.fiber_span.modify`                                     |
| `terminate_fiber_span`                | `orchestrator.optical.workflows.optical_pipe.fiber_span.terminate`                                  |
| `validate_fiber_span`                 | `orchestrator.optical.workflows.optical_pipe.fiber_span.validate`                                   |
| `create_fiber_patch`                  | `orchestrator.optical.workflows.optical_pipe.fiber_patch.create`                                    |
| `modify_fiber_patch`                  | `orchestrator.optical.workflows.optical_pipe.fiber_patch.modify`                                    |
| `terminate_fiber_patch`               | `orchestrator.optical.workflows.optical_pipe.fiber_patch.terminate`                                 |
| `validate_fiber_patch`                | `orchestrator.optical.workflows.optical_pipe.fiber_patch.validate`                                  |
| `create_leased_spectrum`              | `orchestrator.optical.workflows.optical_pipe.leased_spectrum.create`                                |
| `modify_leased_spectrum`              | `orchestrator.optical.workflows.optical_pipe.leased_spectrum.modify`                                |
| `terminate_leased_spectrum`           | `orchestrator.optical.workflows.optical_pipe.leased_spectrum.terminate`                             |
| `validate_leased_spectrum`            | `orchestrator.optical.workflows.optical_pipe.leased_spectrum.validate`                              |
| `create_optical_spectrum`             | `orchestrator.optical.workflows.optical_spectrum_service.create_optical_spectrum`                   |
| `modify_optical_spectrum`             | `orchestrator.optical.workflows.optical_spectrum_service.modify_optical_spectrum`                   |
| `terminate_optical_spectrum`          | `orchestrator.optical.workflows.optical_spectrum_service.terminate_optical_spectrum`                |
| `validate_optical_spectrum`           | `orchestrator.optical.workflows.optical_spectrum_service.validate_optical_spectrum`                 |
| `create_optical_digital_service`      | `orchestrator.optical.workflows.optical_digital_service.create_optical_digital_service`             |
| `modify_optical_digital_service`      | `orchestrator.optical.workflows.optical_digital_service.modify_optical_digital_service`             |
| `terminate_optical_digital_service`   | `orchestrator.optical.workflows.optical_digital_service.terminate_optical_digital_service`          |
| `validate_optical_digital_service`    | `orchestrator.optical.workflows.optical_digital_service.validate_optical_digital_service`           |
| `create_optical_module_location`      | `orchestrator.optical.workflows.optical_location.create`                                            |
| `modify_optical_module_location`      | `orchestrator.optical.workflows.optical_location.modify`                                            |
| `terminate_optical_module_location`   | `orchestrator.optical.workflows.optical_location.terminate`                                         |
| `validate_optical_module_location`    | `orchestrator.optical.workflows.optical_location.validate`                                          |

### 2. Define your own product type that has-a the shipped block (composition + optional anti-corruption layer)

You are free to model your subscription as you see fit **outside** the shipped blocks, as long as your model has a
field that is the shipped block. The shipped blocks must always be part of your model and are persisted with it.
This is needed because the module's logic read the database by shipped block name and thus you cannot simply create the
shipped blocks in-memory during steps execution. You are free to sync the same information outside the shipped blocks
using thin "anti-corruption" wiring code that links your custom fields to the shipped fields (e.g. using `computed_fields`).

Your product block chain references the shipped block's lifecycle variants in the matching lifecycle slots:

```python
# mywfo/models.py
from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import (
    OpticalModulePacketNode,
    OpticalModulePacketNodeInactive,
    OpticalModulePacketNodeProvisioning,
)

class RouterBlockInactive(ProductBlockModel, product_block_name="RouterBlock"):
    my_own_field: str | None = None
    interface_for_the_optical_module: OpticalModulePacketNodeInactive

class RouterBlockProvisioning(RouterBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    my_own_field: str
    interface_for_the_optical_module: OpticalModulePacketNodeProvisioning

class RouterBlock(RouterBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    my_own_field: str
    interface_for_the_optical_module: OpticalModulePacketNode


class RouterSubscriptionInactive(SubscriptionModel, is_base=True):
    router: RouterBlockInactive

class RouterSubscriptionProvisioning(RouterSubscriptionInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    router: RouterBlockProvisioning

class RouterSubscription(RouterSubscriptionProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    router: RouterBlock
```

(Remember the persistence rule of orchestrator-core: every concrete block class redeclares every field it inherits,
including the shipped block field.)

The shipped workflows of path 1 are not reusable here — they are bound to the shipped subscription models. You
compose your own workflows from the shipped **parts**: the importable form generators and the step lists. The shipped
block steps never know your model: they bind to the state key `optical_node_block` (see "State contract" below), so
you wire your block into the state and back out of it — that is the thin anti-corruption wiring:

```python
# mywfo/workflows.py
from functools import partial

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import begin, step
from orchestrator.core.workflows.steps import set_status, store_process_subscription
from orchestrator.core.workflows.utils import create_workflow, modify_workflow
from orchestrator.optical.workflows.optical_node.nokia_flexils.create import (
    create_optical_node_nokia_flexils_form_generator,
    populate_optical_node_nokia_flexils_block,
)
from orchestrator.optical.workflows.optical_node.nokia_flexils.modify import (
    MODIFY_NOKIA_FLEXILS_BLOCK_STEPS,
    modify_optical_node_nokia_flexils_form_generator,
)
from mywfo.models import Router, RouterInactive, RouterProvisioning

@step("Construct my router")
def construct_my_router(
    product, customer_id, location_id, my_own_field, optical_node_role, pqdn,
    optical_node_software_version, optical_flexils_gmpls_id, optical_flexils_target_id,
):
    router = RouterInactive.from_product_id(product_id=product, customer_id=customer_id)
    router.router.my_own_field = my_own_field
    # Anti-corruption point: mirror the flat form keys into the shipped block
    populate_optical_node_nokia_flexils_block(
        optical_node_block=router.router.for_the_optical_module,
        location_id=location_id,
        optical_node_role=optical_node_role,
        pqdn=pqdn,
        optical_node_software_version=optical_node_software_version,
        optical_flexils_gmpls_id=optical_flexils_gmpls_id,
        optical_flexils_target_id=optical_flexils_target_id,
    )
    router = RouterProvisioning.from_other_lifecycle(router, SubscriptionLifecycle.PROVISIONING)
    return {"subscription": router}

@step("Wire my block into the state")
def load_my_router_block(subscription):
    return {"optical_node_block": subscription.for_the_optical_module}

@create_workflow(
    initial_input_form=partial(create_optical_node_nokia_flexils_form_generator, product_name="My Router")
)
def create_my_router():
    return (
        begin
        >> construct_my_router
        >> store_process_subscription()
    )

@modify_workflow(
    initial_input_form=partial(
        modify_optical_node_nokia_flexils_form_generator,
        subscription_model=Router,
        block_field_name="for_the_optical_module",
    )
)
def modify_my_router():
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> load_my_router_block                       # thin wiring: block into the state
        >> MODIFY_NOKIA_FLEXILS_BLOCK_STEPS           # updates and persists the shipped block
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )
```

Notes:

- The shipped `MODIFY_*_BLOCK_STEPS` lists are the same steps shipped for path 1; they read the block from the
  state and end with a step that persists it, because workflow steps reload the subscription from the database and
  would otherwise lose the mutations. The `CREATE_*_BLOCK_STEPS` lists exist for consumers that want to populate the
  block as separate steps (construct the inactive subscription, put the block in the returned `state` under
  `optical_node_block`, run the block steps, then transition); populating the block inside the construct step as
  shown above keeps the same guarantees with fewer moving parts.
- The shipped create form is reusable as-is: it emits the flat `optical_*` keys the shipped steps consume. If you
  write your own form, you must either emit the same keys or write your own steps. The shipped terminate/validate
  forms and step lists compose the same way.
- The shipped forms are **page sequences** (a `FormGenerator` that yields the shipped `FormPage` classes in order and
  returns the collected user input as a flat dict), not hook-laden generators. Consumers compose their own form
  generator by yielding from the shipped pages in one line, optionally interleaving their own pages, and finishing
  with the shipped summary helpers (`create_summary_form` / `modify_summary_form`). The `optical_location` family is
  the reference implementation:

  ```python
  # mywfo/forms.py
  from orchestrator.optical.workflows.optical_location.create import create_optical_module_location_form_pages
  from orchestrator.optical.workflows.shared import create_summary_form

  def my_create_form_generator(product_name):
      user_input_dict = yield from create_optical_module_location_form_pages(product_name)  # all shipped pages
      user_input_dict.update((yield MyOwnFormPage).model_dump())                            # own pages in between
      yield from create_summary_form(user_input_dict, product_name, ["customer_id", ..., "my_own_field"])
      return user_input_dict
  ```

  For modify, the shipped page sequence is prefilled from the subscription and is composed the same way:
  `user_input_dict = yield from modify_optical_module_location_form_pages(subscription, block_field_name="router")`.
  The page factories returning individual prefilled pages (e.g. `modify_optical_module_location_form(subscription,
  block_field_name)`) are exported for consumers that pick pages individually.
- How much of your own information you keep is up to you: you can mirror your own fields into the shipped block (a
  thin anti-corruption layer, representing some information twice — in your shape and in the shipped block) or store
  everything in the shipped block only. Both are the same consumption path with different amounts of duplication;
  the transformation logic of the anti-corruption layer is yours to write and maintain. The module never depends on
  your model: it only sees the shipped block.
- You must register your own product type in the subscription model registry (as with any WFO product).

## State contract

The shipped block steps take the shipped block from the workflow state under a documented key. Consumers put their
composed block in the state under that key (one small step); the block steps read and write it, and the shipped
persistence step saves it back into the owner subscription.

| State key                            | Block                                         | Used by                                                        |
|--------------------------------------|-----------------------------------------------|----------------------------------------------------------------|
| `optical_node_block`                 | any shipped Optical Node vendor block         | optical node create/modify block steps                         |
| `optical_coherent_pluggable_block`   | the shipped `OpticalCoherentPluggableBlock`   | coherent pluggable create/modify block steps, validate step    |
| `optical_module_location_block`      | the shipped `OpticalModuleLocationBlock`      | optical module location create/modify block steps, validate step |

The constants are exported as `OPTICAL_NODE_BLOCK_STATE_KEY`, `OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY` and
`OPTICAL_LOCATION_BLOCK_STATE_KEY`. The flat form keys
(`pqdn`, `optical_management_ip`, `optical_loopback_ip`, `optical_flexils_*`, `optical_node_role`,
`optical_node_software_version`, `location_id`, `customer_id`) are the second half of the contract: the shipped forms
emit them and the shipped steps consume them.

## Configuring the customer selection

Every create and modify workflow of this module asks the user to pick the customer of the subscription. Which
subscriptions qualify as customers is deployment-specific, so the `Choice` selector is built by a function that you
define in your own code. The chosen option value is set as the subscription `customer_id`.

Define the function anywhere in your WFO code:

```python
from pydantic_forms.validators import Choice

def customer_choice() -> type[Choice]:
    customers = {...}  # e.g. your active "Customer" subscriptions
    return Choice("Select a customer", zip(customers.keys(), customers.items(), strict=False))
```

Then wire it up in one of two ways:

1. **Environment variable** (recommended) — set `OPTICAL_CUSTOMER_CHOICE` to the import path of the function, e.g.
   `OPTICAL_CUSTOMER_CHOICE="mywfo.customers:customer_choice"`.
2. **At application startup** — call the registration function:

   ```python
   from orchestrator.optical.workflows.customer import register_customer_choice
   register_customer_choice(customer_choice)
   ```

The function is called once per form generation, takes no arguments, and must return a `type[Choice]` whose option
values are the customer ids (UUID strings). If it is not configured, the workflows raise a clear error when the form
is opened.

## Status of the port

Every product family ships the ready-to-use workflows of its shipped product types (the 40 workflows listed above)
plus the importable parts (the FormPages of the shipped forms and the step lists). There are no workflow factories or
hooks; the shipped workflows are plain decorated functions bound to the shipped subscription models, so they are only
valid when the shipped product types are used as-is. The shipped workflows are built using the same shipped forms and
steps that can also be used on custom subscriptions as long as they have-a the shipped blocks and use the appropriate
`state key` listed in the table above. The `optical_location` family is the reference implementation of the FormPage
consumption model (shipped page sequences + one-line `yield from` composition, no `extra_form_pages`/
`extra_summary_fields` hooks); the other families still carry the legacy hook-style form generators, mid-port.

Coherent pluggable specifics:

- The create form validates port uniqueness **by shipped block name** (not by product type), so it also guards
  consumer product types that have-a the shipped block. It resolves the selected packet node through
  `packet_node_block_from_subscription` (block-based, from the neutral `orchestrator/optical/db.py`, like the
  Optical Location family): any subscription persisting the shipped packet-node block qualifies — otherwise write
  your own form/validator.
- The subscription description includes the subscription-level part number, so it is only computed by the shipped
  construct step and the shipped-type description refresh step
  (`shared.update_optical_coherent_pluggable_subscription_description`); the shipped block steps never touch
  subscription-level state.
- The shipped modify block steps do not persist a changed `customer_id` (the form still emits it); add your own step
  if your product tracks it.

The `optical_location` family ships the ready-to-use workflows of the shipped `OpticalModuleLocationSubscription`
product type (create/modify/terminate/validate) plus the importable parts: the FormPages of the shipped forms (as page
sequences, e.g. `create_optical_module_location_form_pages(product_name)`, consumed with a one-line
`yield from`) and the block step lists operating on the shipped `OpticalModuleLocationBlock` under the
`optical_module_location_block` state key. The shipped form generators are thin compositions of the shipped pages and
the summary form, without hooks — this family is the reference implementation of the FormPage consumption model. The
shipped modify form offers a `clear location name` checkbox to delete the optional `location_name` field. The family
also ships the location subscription selector `active_location_subscription_selector`; the block-based
`location_block_from_subscription` (used by the shipped optical node workflows) lives in the neutral
`orchestrator/optical/db.py` module.

## Development

* Clone this repository
* On your local implementation of the WFO, run `uv add --editable /this/repo` (or `pip install -e /this/repo`).
