# End-to-end tests

Browser tests run in a Docker container, never on the host desktop. They start the shop in a
thread with an in-process payment gateway, drive headless Chromium with Playwright and are
skipped when Playwright is not installed, so the host `pytest` run ignores them.

```
docker build -t online-shop-shots tools/screenshots
docker run --rm -v "${PWD}:/work" -w /work --entrypoint python online-shop-shots -m pytest -o addopts="" -o pythonpath="src tests" --junitxml=results/e2e.xml tests/e2e
```

`test_order_board.py` buys an order as a customer, drags its card to Confirmed as the admin and
checks that it is still there after a reload, that a customer gets 403 on the board, and that
the five columns are reachable at 400 pixels.
