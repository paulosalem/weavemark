import { expect, test } from "@playwright/test";

test("player can start, build, observe simulation feedback, pause, finish, and replay", async ({ page }) => {
  const browserErrors = [];
  page.on("console", (message) => {
    if (message.type() === "error") {
      browserErrors.push(message.text());
    }
  });
  page.on("pageerror", (error) => browserErrors.push(error.message));

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Transit City Swarm" })).toBeVisible();
  await expect(page.getByText("Draw a readable transit organism")).toBeVisible();

  await page.getByRole("button", { name: "Start round" }).click();
  await expect(page.locator("#gameStatus")).toHaveText("Playing");

  await clickWorld(page, 160, 152);
  await clickWorld(page, 424, 160);
  await clickWorld(page, 688, 272);
  await expect(page.locator('[data-stat="stops"]')).toHaveText("3");

  await page.locator("#speedButton").click();
  await expect(page.locator("#speedButton")).toHaveText("2x speed");
  await page.waitForTimeout(1800);

  const activeSnapshot = await page.evaluate(() => window.__transitCitySwarm.getSnapshot());
  expect(activeSnapshot.agents + activeSnapshot.served + activeSnapshot.missed).toBeGreaterThan(0);
  expect(activeSnapshot.budget).toBeLessThan(260);

  await page.keyboard.press("Space");
  await expect(page.locator("#gameStatus")).toHaveText("Paused");
  await page.keyboard.press("Space");
  await expect(page.locator("#gameStatus")).toHaveText("Playing");

  await page.getByRole("button", { name: "Finish shift" }).click();
  await expect(page.locator("#resultsScreen")).toBeVisible();
  await expect(page.getByRole("button", { name: "Play again" })).toBeVisible();
  await page.screenshot({ path: "test-results/transit-city-swarm-smoke.png", fullPage: true });

  await page.getByRole("button", { name: "Play again" }).click();
  await expect(page.locator("#gameStatus")).toHaveText("Playing");
  await expect(page.locator('[data-stat="stops"]')).toHaveText("0");

  expect(browserErrors).toEqual([]);
});

async function clickWorld(page, x, y) {
  const metrics = await page.locator("#gameCanvas").evaluate((canvas) => {
    const rect = canvas.getBoundingClientRect();
    const worldWidth = 960;
    const worldHeight = 640;
    const scale = Math.min(rect.width / worldWidth, rect.height / worldHeight);
    return {
      offsetX: (rect.width - worldWidth * scale) / 2,
      offsetY: (rect.height - worldHeight * scale) / 2,
      scale
    };
  });

  await page.locator("#gameCanvas").click({
    position: {
      x: metrics.offsetX + x * metrics.scale,
      y: metrics.offsetY + y * metrics.scale
    }
  });
}
