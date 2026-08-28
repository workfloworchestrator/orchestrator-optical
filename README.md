# Workflow Orchestrator (WFO) Optical Module

## Project Overview

The WFO Optical Module is a Python module that can be installed as a dependency for
[WFO](https://workfloworchestrator.org) users that want to integrate with their optical equipment. This project is
built on top of [`orchestrator-core`](https://github.com/workfloworchestrator/orchestrator-core).

## Installation

To use the models and services from this module, you will need to make some changes to your local implementation of the
WFO. Please follow the steps below to install the WFO Optical module, including some file edits:

1. `uv add orchestrator-optical`
2. Provision the shipped catalog in your database. See "Database migrations" below: until the module reaches a
   stable release this is done with the orchestrator-core CLI wizards; from the first stable release the module ships
   the catalog as Alembic migrations.
3. The module is currently a work in progress (ported from a GARR-specific implementation): the model files are still
   being finalized and are subject to change between releases. See the "Consumption model" section below for how to
   decouple your own products from those changes.

## Database migrations

The module ships **coded programmatic migrations**: its catalog (products, product blocks, resource types and the
shipped workflows) is provisioned as data migrations, exactly like orchestrator-core provisions its own domain. The
module owns **no tables** — everything lives in the core catalog tables.

### Until the first stable release (module < 1.0)

The models are still being finalized and shipped Alembic revisions would have to be rewritten between releases
(rewriting a shipped revision breaks consumers mid-upgrade). Until 1.0 the shipped `versions/schema` directory is
**empty** and consumers provision the catalog with the orchestrator-core CLI, the same way they provision their own
products:

```shell
orchestrator db migrate-domain-models -m "add optical products"
orchestrator db migrate-workflows -m "add optical workflows"
orchestrator db upgrade head
```

The diff-based wizards scan the whole `SUBSCRIPTION_MODEL_REGISTRY` (the module's models plus your own), so set
`SKIP_MODEL_FOR_MIGRATION_DB_DIFF` to the optical product names if you run the wizards for your own products as well,
to avoid the module's products being picked up by your diffs.

### From the first stable release (module >= 1.0) 

> [!TODO]
> We need to find a way to version the models and ship the migrations as code. The following is just an idea.

The module ships one generated Alembic revision per release in
`orchestrator.optical.migrations.versions.schema`, chained linearly onto a pinned orchestrator-core schema revision
(the revision ids are deterministic — the same models always produce the same revision). Consumers:

1. Point Alembic at the shipped directory. Either add the installed package's
   `orchestrator/optical/migrations/versions/schema` directory to your `alembic.ini` `version_locations`, or call the
   shipped helper from your migration entrypoint:

   ```python
   from alembic.config import Config
   from orchestrator.optical.migrations import add_optical_module_migrations

   config = Config("alembic.ini")
   add_optical_module_migrations(config)
   ```

2. Merge the optical head with your `data` head **once** after installing:

   ```shell
   orchestrator db merge <your data head> <optical head>
   ```

3. `orchestrator db upgrade head` — from then on every upgrade is a plain `upgrade head`.

The module's migrations are **generated, never hand-written**: the pipeline in
`orchestrator.optical.migrations.generate` derives the catalog directly from the shipped models (the models are the
single source of truth) and discovers the shipped workflows from the workflows package. Maintainers run it to commit
the baseline at 1.0 and each later release's delta:

```shell
python -m orchestrator.optical.migrations --commit     # write the baseline into versions/schema
python -m orchestrator.optical.migrations --verify    # apply pending migrations, fail on model drift
```

`--verify` is the drift gate: it applies the migrations to a scratch database and re-runs the orchestrator-core
domain-model diff, failing if the applied catalog is not a faithful projection of the shipped models. It is exercised
end to end by the DB-backed test suite (`test/test_migrations.py`, `test/conftest.py`), which provisions the test
database exactly the way a consumer would.

## Consumption model

The module ships **concrete product blocks** (e.g. `OpticalFiberSpanBlock`), the matching
subscription product types, hardware abstraction layer `hal/` services, the **ready-to-use workflows of the shipped product types** (one
create/modify/terminate/validate per product) and the **parts of the workflows** (the FormPages of the shipped forms,
as page sequences, and the step lists).

> The module expects you to use the shipped concrete blocks as a **shared interface** that you compose with your own model.

### Architecture

The module is strictly layered: `products/` (blocks and subscription models) → `hal/` (device-facing logic) →
`workflows/` (orchestration), with `services/` (device clients) behind `hal/`. **Blocks are the shared
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

You are free to model your subscription as you see fit as long as your model has a
field that is the shipped block. The shipped blocks must always be part of your model and persisted with it.
This is needed because the module's logic needs to read the database by shipped `product_block_name`.
You are invited to duplicate the information saved in the shipped blocks also inside your own models in your own fashion
and to use thin "anti-corruption" wiring code that links your custom fields to the shipped fields (e.g. using `computed_fields`).
This way the changes to this module's domain models will always be clearly decoupled from your models and your logic.

For example, if you already have subscriptions to manage your routers and you want to use this module (that needs
to access the routers to configure the optical coherent pluggables), then you must add the `OpticalModulePacketNode` block
to your existing `RouterBlock`:

```python
# in your product_blocks/ dir 
from orchestrator.optical.products.product_blocks.optical_packet_node import (
    OpticalModulePacketNode,
    OpticalModulePacketNodeInactive,
    OpticalModulePacketNodeProvisioning,
)

class RouterBlockInactive(ProductBlockModel, product_block_name="RouterBlock"):
    field1: str | None = None
    # ...
    # you must add this block
    optical_module_block: OpticalModulePacketNodeInactive

class RouterBlockProvisioning(RouterBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    field1: str
    optical_module_block: OpticalModulePacketNodeProvisioning

class RouterBlock(RouterBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    field1: str
    optical_module_block: OpticalModulePacketNode
```

The shipped workflows of path 1 are not reusable here — they are bound to the shipped subscription models. Thus, you
compose your own workflows from the shipped **parts**: the importable form generators and the step lists. The shipped
block steps never know your model: they bind to the state key `optical_module_block` (see "State contract" below), so
you wire your block into the state and back out of it — that is the thin anti-corruption wiring:

```python
# TODO: provide example of create workflow using the shipped form pages and steps.
```

Notes:

- The public surface of a family is its **form pages** and its **block-level `StepList`s**.
  Every step in a `*_BLOCK_STEPS` list operates on the block found in the
  state under `optical_module_block`: the `*_BLOCK_STEPS` lists are fully block-level and self-contained with the last step
  persisting the block. The block is assumed to always be in the `PROVISIONING` status. Therefore your construct step builds
  your subscription and puts the composed block in the state, and you run the list. The
  `*_BLOCK_STEPS` lists are the same steps used for path 1; they read the block from the state and end
  with a step that persists it, because workflow steps reload the subscription from the database and would
  otherwise lose the mutations.
- The shipped form pages are reusable as-is: they emit the flat `optical_*` keys the shipped steps consume. If you
  write your own form, you must either emit the same keys or write your own steps.
- The shipped forms are **page sequences** (a `FormGenerator` that yields the shipped `FormPage` classes in order and
  returns the collected user input as a flat dict). Consumers compose their own form
  generator by `yield from`-ing the shipped pages in one line and optionally finishing
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
  `user_input_dict = yield from modify_optical_module_location_form_pages(subscription, block_field_name="optical_location")`.
- How much of your own information you keep is up to you: you can mirror your own fields into the shipped block (a
  thin anti-corruption layer, representing some information twice — in your shape and in the shipped block) or store
  everything in the shipped block only. Both are the same consumption path with different amounts of duplication and coupling;
  the transformation logic of the anti-corruption layer is yours to write and maintain. **The module never depends on
  your model: it only sees the shipped block.**

## State contract

The shipped block steps take the shipped block from the workflow state always under the same key: `optical_module_block`. Consumers put their
composed block in the state under this key (one small step); the block steps read and write it, and the shipped
persistence step saves it back into the owner subscription.

## Configuring the customer selection

Every create and modify workflow of this module asks the user to pick the customer of the subscription. Which
subscriptions qualify as customers is deployment-specific, so the `Choice` selector is built by a function that you
define in your own code. The chosen option value is set as the subscription `customer_id`.

The function is called once per form generation, takes no arguments, and must return a `type[Choice]` whose option
values are the customer ids (UUID strings). If it is not configured, the workflows raise a clear error when the form
is opened.

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

### Where the customer is collected

The shipped **create** and **modify** page sequences (`create_<product>_form_pages` / `modify_<product>_form_pages`)
do **not** collect the customer because customer management it is outside the scope of this module: they emit only the `optical_*` 
(and `location_id`/`node_a_id`/...) state keys. However, complete workflows (not just steps) require the `customer_id`,
and thus, when using the subscriptions/workflows as-is, the customer is collected separately by the shipped form
generators through the reusable page sequence
`customer_choice_form_page(include=None)` in `orchestrator.optical.workflows.customer` — a single page with one
`customer_id` field built from your `customer_choice()` function.

When you compose your own form generator (e.g. for a product type that has-a the shipped block), collect the customer
yourself — either by yielding from `customer_choice_form_page` in one line or by defining your own customer page on
top of `customer_choice_selector(include=...)` (pass `include` the current `customer_id` on a modify):

```python
from orchestrator.optical.workflows.customer import customer_choice_form_page

def my_create_form_generator(product_name):
    user_input_dict = yield from customer_choice_form_page(title=product_name)
    user_input_dict.update((yield from create_optical_module_location_form_pages(product_name)))
    ...
```

`customer_choice_form_page` returns `{"customer_id": ...}`, which the shipped steps consume together with the
`optical_*` keys returned by the page sequence.


## Status of the port

The `optical_location` and `optical_node` families are the reference implementations. Other workflows are mid-port
and will change.


## Development

* Clone this repository
* On your local implementation of the WFO, run `uv add --editable /this/repo` (or `pip install -e /this/repo`).
