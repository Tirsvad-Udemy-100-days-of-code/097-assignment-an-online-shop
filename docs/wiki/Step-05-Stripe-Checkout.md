**English** · [Dansk](Step-05-Stripe-Checkout-da) · [Bahasa Malaysia](Step-05-Stripe-Checkout-ms)

# Step 5: Stripe checkout

The shopper pays through Stripe Checkout in test mode, and only a paid session creates an order.

![Step 5](https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-nnline-shop/raw/branch/main/docs/screenshots/step-05.png)

## The flow

1. The basket page has a **Checkout** button. It posts to the shop, which creates a Checkout Session at Stripe with one line item per basket line and sends the browser to Stripe's payment page.
2. After paying, Stripe sends the shopper back to a success address that carries the session id.
3. The shop does not trust that address. It asks Stripe for the session and creates an order only when Stripe says it is paid and the session belongs to the signed-in user. Opening the same address twice creates one order, because the session id is unique.
4. If the shopper cancels, the basket is kept and no order is created.

A new order has the status "Needs confirmation". The basket is emptied only after the order is saved.

## A port and a fake

The shop talks to a `PaymentGateway` port. The Stripe adapter calls the REST API with `urllib`, form-encoding the nested fields. Tests use a fake gateway and, for the adapter, a small local server that plays Stripe, so no test touches the network.

## Test mode and keys

The test keys are read from a local `stripe.env` file that git ignores. The shop refuses any key that is not a test key. Keys are never printed, logged or put in an error message, and without the file the shop reads the environment variables `PUBLISHABLE_KEY` and `SECRET_KEY`, or, with neither, still starts with the Checkout button hidden. In test mode you pay with the card `4242 4242 4242 4242`, any future date and any CVC.

## What I learned

- Never create an order from the return address alone; ask the provider what happened.
- A unique session id makes the success page safe to reload.
- A secret needs three rules: kept out of git, kept out of output, and checked for the right mode before use.
