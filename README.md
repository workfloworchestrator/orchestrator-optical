# Workflow Orchestrator (WFO) Optical Module

## Project Overview

The WFO Optical Module is a Python module that can be installed as a dependency for
[WFO](https://workfloworchestrator.org) users that want to integrate with their optical equipment. This project is
built on top of [`orchestrator-core`](https://github.com/workfloworchestrator/orchestrator-core).

## Installation

To use the models and services from this module, you will need to make some changes to your local implementation of the
WFO. Please follow the steps below to install the WFO Optical module, including some file edits:

1. `uv add orchestrator-optical`
2. Generate a database migration for this module in your local `migrations` setup (e.g. via the orchestrator-core
shell commands). This package no longer ships a migrations module, so no module hook needs to be added.
3. The module is currently a work in progress (ported from a GARR-specific implementation): the model files are still
being finalized and are subject to change between releases. Consumer-facing customization guidance (e.g. which models
to subclass) will be provided once the port stabilizes.

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


## Declaring the workflows

This module does not register any workflow itself: every workflow is shipped as a **factory function** that returns
the decorated workflow, whose name is the shipped workflow name (e.g. `create_fiber_span_workflow()` returns the
workflow `create_fiber_span`). Consumers declare one workflow per shipped workflow in their own code — a 1:1 mirror
of the shipped set — and register them via `register_workflows()`. The shipped workflow names are listed in
`orchestrator.optical.workflows.SHIPPED_WORKFLOW_NAMES`.

The minimal all-defaults declaration looks like this:

```python
# mywfo/workflows.py
from orchestrator.optical.workflows import register_workflows
from orchestrator.optical.workflows.optical_pipe.fiber_span.create import create_fiber_span_workflow

create_fiber_span = create_fiber_span_workflow()

register_workflows(__name__)
```

Factories can be extended with hooks. A realistic fiber span create with all four hooks:

```python
from orchestrator.core.workflow import begin, step
from orchestrator.core.forms import FormPage
from pydantic import Annotated, Field
from pydantic_forms.types import State

class SpanTicketForm(FormPage):
    oss_ticket: Annotated[str, Field(title="OSS ticket id")]

@step("Register the fiber span in my inventory")
def register_span_in_my_inventory(subscription) -> State:
    ...

create_fiber_span = create_fiber_span_workflow(
    pre_steps=begin >> my_precheck,
    post_steps=begin >> register_span_in_my_inventory,
    extra_form_pages=[SpanTicketForm],
    extra_summary_fields=["oss_ticket"],
)
```

(Note: `my_precheck` is your own `@step`-decorated function, not shown here.)

Hooks and parameters:

- Every factory accepts `pre_steps` and `post_steps`, plus `**kwargs` forwarded to the WFO workflow decorator
  (`create_workflow`, `modify_workflow`, etc.). Create and modify factories additionally accept `extra_form_pages`
  and `extra_summary_fields`; terminate factories additionally accept `extra_form_pages`.
- Hook contract: `pre_steps` run before any shipped step — for create, the form data is in the state but there is
  no subscription yet; for modify/terminate, the subscription is loaded and still unsynced. `post_steps` run after
  all shipped steps, while the subscription is still unsynced and before it flips to ACTIVE/TERMINATED.
- Extra form fields (from `extra_form_pages`) automatically flow into the workflow state and can be consumed by
  your steps by parameter name.
- `register_workflows(__name__)` must be called at the end of the module that declares the workflows; missing
  declarations are logged as warnings. It raises `TypeError` if an attribute is not a `Workflow` instance (e.g. the
  factory function itself was re-exported instead of its result).
- Terminate workflows have no summary form and thus no `extra_summary_fields`: extra form pages are shown after the
  shipped confirmation page. Validate workflows have no input forms at all and accept only `pre_steps`/`post_steps`.


## Development

* Clone this repository
* On your local implementation of the WFO, run `uv add --editable /this/repo` (or `pip install -e /this/repo`).
