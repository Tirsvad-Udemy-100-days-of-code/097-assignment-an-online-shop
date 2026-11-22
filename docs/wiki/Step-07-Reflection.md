**English** · [Dansk](Step-07-Reflection-da) · [Bahasa Malaysia](Step-07-Reflection-ms)

# Step 7: Reflection

## How I approached the project

I planned first. The business case, the stakeholders, the project plan and seven milestones were written and reviewed before any code, and each milestone went through one pull request with its own review record. The code is in four layers (domain, application, infrastructure, presentation), so the shop rules do not depend on Flask, SQLite or Stripe, and most of the 340 tests run without a browser. I chose a Kanban board for the orders because an order moves through a few clear steps: needs confirmation, confirmed, being packed, shipped and delivered. A board shows the whole queue at a glance, so the owner sees what to do next and moves an order forward with a drag.

## What was easy

The domain rules (money in cents, the basket, the order statuses) and the SQLite repositories. Once the ports existed, fakes made them quick to test.

## What was hard

The order board with drag and drop that keeps positions in the database, and Stripe checkout, which has to be tested without real keys or real payments. CI also caught what my local checks missed: a fake `sk_live_` key in a test tripped the secret scan, and SQL built from f-strings tripped the code scan. Every query is a plain literal with `?` placeholders. User input only travels as a bound value, never inside the SQL text. The scans watch for this too.

## How I might improve for the next project

Run the same scans CI runs before every push, look at a real screenshot as soon as a page exists, and keep the plan and the code in step as I go.

## My biggest learning

A decision that changes in the middle of a project, here the switch from the standard library to Flask, is cheapest when it is written down first in an ADR and the plan, and only then coded. A bug such as `site.update` rendering a dict method in a template is found by looking at a real screenshot, not by the unit tests.

## What I would do differently

Settle the framework before the first milestone, and write the SQL as plain literals with placeholders from the first repository.
