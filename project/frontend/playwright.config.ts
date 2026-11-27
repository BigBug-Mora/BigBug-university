import { defineConfig, devices } from "@playwright/test";
import { appEnvironment, appOrigin, fixtureOrigin } from "./tests/fixture-settings.mjs";

export default defineConfig({
  testDir: "./tests",
  workers: 1,
  use: { ...devices["Desktop Chrome"], baseURL: appOrigin },
  webServer: [
    { command: "node tests/oidc-fixture.mjs", url: fixtureOrigin },
    {
      command: "npm run start",
      url: appOrigin,
      env: { ...appEnvironment, HOSTNAME: "127.0.0.1", PORT: new URL(appOrigin).port },
    },
  ],
});
