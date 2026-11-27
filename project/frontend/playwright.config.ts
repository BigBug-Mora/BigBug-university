import { defineConfig, devices } from "@playwright/test";
import { appEnvironment, appOrigin, fixtureOrigin, identityStack } from "./tests/fixture-settings.mjs";

export default defineConfig({
  testDir: "./tests",
  testMatch: identityStack ? "**/*-stack.spec.ts" : "**/sign-in.spec.ts",
  workers: 1,
  use: {
    ...devices["Desktop Chrome"],
    baseURL: appOrigin,
    launchOptions: identityStack ? {
      args: ["--host-resolver-rules=MAP identity-fixture 127.0.0.1", "--no-proxy-server"],
    } : undefined,
  },
  webServer: identityStack ? undefined : [
    { command: "node tests/oidc-fixture.mjs", url: fixtureOrigin },
    {
      command: "npm run start",
      url: appOrigin,
      env: { ...appEnvironment, HOSTNAME: "127.0.0.1", PORT: new URL(appOrigin).port },
    },
  ],
});
