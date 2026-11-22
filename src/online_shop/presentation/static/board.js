"use strict";

/**
 * The order board: plain JavaScript, no libraries. It loads the columns from the
 * board API, moves a card with HTML5 drag and drop or the select on the card,
 * shows the move at once and sends it; when the server refuses, the move is
 * undone and a message is shown. The DOM is built with textContent only.
 */

const meta = (name) => document.querySelector(`meta[name="${name}"]`).content;

const config = {
  csrf: meta("csrf-token"),
  boardUrl: meta("board-api"),
  moveUrl: meta("board-move-api"),
  moveFailed: meta("board-move-failed"),
  loadFailed: meta("board-load-failed"),
  moveTo: meta("board-move-to"),
  order: meta("board-order"),
  empty: meta("board-empty"),
};

const state = { columns: [] };
const drag = { orderId: null };
let sending = Promise.resolve();

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) {
    node.className = className;
  }
  if (text !== undefined) {
    node.textContent = text;
  }
  return node;
}

function showMessage(text) {
  document.getElementById("board-message").textContent = text;
}

async function request(method, url, body) {
  const headers = { Accept: "application/json" };
  const options = { method, headers, credentials: "same-origin" };
  if (method !== "GET") {
    headers["X-CSRF-Token"] = config.csrf;
  }
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(response.statusText || String(response.status));
  }
  return response.json();
}

/** Where a card is: the index of its column and of its place in it. */
function locate(orderId) {
  for (const [columnIndex, column] of state.columns.entries()) {
    const cardIndex = column.cards.findIndex((card) => card.order_id === orderId);
    if (cardIndex !== -1) {
      return { columnIndex, cardIndex };
    }
  }
  return null;
}

/** Move a card in the local state; the index counts the target without the card. */
function moveLocally(orderId, status, index) {
  const from = locate(orderId);
  const target = state.columns.find((column) => column.status === status);
  if (from === null || target === undefined) {
    return;
  }
  const [card] = state.columns[from.columnIndex].cards.splice(from.cardIndex, 1);
  target.cards.splice(Math.max(0, Math.min(index, target.cards.length)), 0, card);
  for (const column of state.columns) {
    column.count = column.cards.length;
  }
}

/** Move at once, then tell the server; on failure put everything back. */
function moveOrder(orderId, status, index, refocus) {
  const snapshot = structuredClone(state.columns);
  moveLocally(orderId, status, index);
  render();
  if (refocus) {
    focusSelect(orderId);
  }
  showMessage("");
  sending = sending.then(async () => {
    try {
      await request("POST", config.moveUrl, { order_id: orderId, status, index });
    } catch {
      state.columns = snapshot;
      render();
      if (refocus) {
        focusSelect(orderId);
      }
      showMessage(config.moveFailed);
    }
  });
  return sending;
}

function renderMoveSelect(card, column) {
  const label = element("label", "card-move");
  label.append(element("span", "visually-hidden", `${config.moveTo} (${config.order} #${card.order_id})`));
  const select = element("select", "card-move-select");
  select.dataset.orderId = String(card.order_id);
  for (const target of state.columns) {
    const option = element("option", "", target.status);
    option.value = target.status;
    option.selected = target.status === column.status;
    select.append(option);
  }
  select.addEventListener("change", () => {
    const target = state.columns.find((entry) => entry.status === select.value);
    const others = target.cards.filter((entry) => entry.order_id !== card.order_id);
    moveOrder(card.order_id, select.value, others.length, true);
  });
  label.append(select);
  return label;
}

function renderCard(card, column) {
  const node = element("li", "board-card");
  node.draggable = true;
  node.dataset.orderId = String(card.order_id);
  node.addEventListener("dragstart", (event) => startDrag(event, card.order_id, node));
  node.addEventListener("dragend", endDrag);
  const items = element("ul", "card-items");
  for (const item of card.items) {
    items.append(element("li", "", item));
  }
  const created = element("time", "card-created", card.created);
  created.dateTime = card.created_at;
  node.append(
    element("strong", "card-number", `${config.order} #${card.order_id}`),
    element("span", "card-customer", card.customer_email),
    items,
    element("span", "card-total", card.total),
    created,
    renderMoveSelect(card, column),
  );
  return node;
}

function renderColumn(column) {
  const section = element("section", "board-column");
  section.dataset.status = column.status;
  section.addEventListener("dragover", (event) => overColumn(event, section));
  section.addEventListener("dragleave", (event) => leaveColumn(event, section));
  section.addEventListener("drop", (event) => dropOnColumn(event, column.status, section));
  const header = element("header", "column-header");
  const count = element("span", "column-count", String(column.cards.length));
  count.setAttribute("aria-label", `${column.cards.length}`);
  header.append(element("h2", "column-title", column.status), count);
  const list = element("ul", "board-cards");
  list.setAttribute("aria-label", column.status);
  for (const card of column.cards) {
    list.append(renderCard(card, column));
  }
  if (column.cards.length === 0) {
    list.append(element("li", "board-empty", config.empty));
  }
  section.append(header, list);
  return section;
}

function render() {
  document.getElementById("board").replaceChildren(...state.columns.map(renderColumn));
}

/** Keep the keyboard on the select of a card after the board is drawn again. */
function focusSelect(orderId) {
  const select = document.querySelector(`select[data-order-id="${orderId}"]`);
  if (select !== null) {
    select.focus();
  }
}

function startDrag(event, orderId, node) {
  drag.orderId = orderId;
  event.dataTransfer.effectAllowed = "move";
  event.dataTransfer.setData("text/plain", String(orderId));
  requestAnimationFrame(() => node.classList.add("dragging"));
}

function endDrag() {
  drag.orderId = null;
  document.querySelectorAll(".dragging, .drop-target").forEach((node) =>
    node.classList.remove("dragging", "drop-target"));
}

/** Number of cards whose centre is above the pointer, not counting the dragged one. */
function insertIndex(list, pointerY) {
  let index = 0;
  for (const card of list.querySelectorAll(".board-card")) {
    if (card.classList.contains("dragging")) {
      continue;
    }
    const box = card.getBoundingClientRect();
    if (box.top + box.height / 2 < pointerY) {
      index += 1;
    }
  }
  return index;
}

function overColumn(event, section) {
  if (drag.orderId === null) {
    return;
  }
  event.preventDefault();
  event.dataTransfer.dropEffect = "move";
  section.classList.add("drop-target");
}

function leaveColumn(event, section) {
  if (!section.contains(event.relatedTarget)) {
    section.classList.remove("drop-target");
  }
}

function dropOnColumn(event, status, section) {
  if (drag.orderId === null) {
    return;
  }
  event.preventDefault();
  const orderId = drag.orderId;
  const index = insertIndex(section.querySelector(".board-cards"), event.clientY);
  endDrag();
  moveOrder(orderId, status, index, false);
}

async function loadBoard() {
  try {
    state.columns = (await request("GET", config.boardUrl)).columns;
    render();
  } catch {
    showMessage(config.loadFailed);
  }
}

loadBoard();
