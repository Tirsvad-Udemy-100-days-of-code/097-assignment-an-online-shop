**English** · [Dansk](Step-06-Order-Kanban-Board-da) · [Bahasa Malaysia](Step-06-Order-Kanban-Board-ms)

# Step 6: Order Kanban board

The shop owner follows every paid order on a Kanban board, and each customer sees the status of their own orders.

![Step 6](https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-online-shop/raw/branch/main/docs/screenshots/step-06.png)

## Status flow

An order moves through five columns: **Needs confirmation**, **Confirmed**, **Being packed**, **Shipped** and **Delivered**. A paid order starts at the end of the first column. The owner drags a card to another column, or within a column to change its place, and the shop saves the new status and position. Positions are renumbered in the source and target column in one transaction, so the order of the cards is the same after a reload.

## The board

The board page is for admins only: a visitor who is not signed in goes to the login page and a customer gets 403. Each card shows the order number, the customer's email, the items and the total. The page uses plain JavaScript and the browser's own drag and drop, with no library. A move is shown at once and then sent to the shop with the CSRF token; if the shop refuses it, the card jumps back and a message is shown. A select on each card does the same move without dragging, for keyboards and phones. At 400 pixels wide the columns scroll sideways.

## Reused from Day 89

The layout and the drag-and-drop idea come from the Day 89 todo list: lists became status columns and cards became orders. The code was rewritten for this shop's dark theme and its own API.

## Customer order history

The Orders page lists the signed-in customer's own orders, newest first, with items, total and a status badge.

## Testing

A browser test in a Docker container drags an order to Confirmed, reloads the page and checks that it stayed there, and that a customer cannot open the board.

## What I learned

- Saving the position as well as the status is what makes a drag survive a reload.
- Doing the move in one transaction keeps the columns consistent.
- A control that does the same thing without dragging makes the board usable on a phone and with a keyboard.
