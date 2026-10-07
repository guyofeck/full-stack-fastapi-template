import { expect, test } from "@playwright/test"
import { createUser } from "./utils/privateApi"
import {
  randomEmail,
  randomItemDescription,
  randomItemTitle,
  randomPassword,
} from "./utils/random"
import { logInUser } from "./utils/user"

test("Items page is accessible and shows correct title", async ({ page }) => {
  await page.goto("/items")
  await expect(page.getByRole("heading", { name: "Items" })).toBeVisible()
  await expect(page.getByText("Create and manage your items")).toBeVisible()
})

test("Add Item button is visible", async ({ page }) => {
  await page.goto("/items")
  await expect(page.getByRole("button", { name: "Add Item" })).toBeVisible()
})

test.describe("Items management", () => {
  test.use({ storageState: { cookies: [], origins: [] } })
  let email: string
  const password = randomPassword()

  test.beforeAll(async () => {
    email = randomEmail()
    await createUser({ email, password })
  })

  test.beforeEach(async ({ page }) => {
    await logInUser(page, email, password)
    await page.goto("/items")
  })

  test("Create a new item successfully", async ({ page }) => {
    const title = randomItemTitle()
    const description = randomItemDescription()

    await page.getByRole("button", { name: "Add Item" }).click()
    await page.getByLabel("Title").fill(title)
    await page.getByLabel("Description").fill(description)
    await page.getByRole("button", { name: "Save" }).click()

    await expect(page.getByText("Item created successfully")).toBeVisible()
    await expect(page.getByText(title)).toBeVisible()
  })

  test("Create item with only required fields", async ({ page }) => {
    const title = randomItemTitle()

    await page.getByRole("button", { name: "Add Item" }).click()
    await page.getByLabel("Title").fill(title)
    await page.getByRole("button", { name: "Save" }).click()

    await expect(page.getByText("Item created successfully")).toBeVisible()
    await expect(page.getByText(title)).toBeVisible()
  })

  test("Search items by title through the API", async ({ page }) => {
    const marker = randomItemTitle()
    const matchingTitle = `${marker} Alpha`
    const otherTitle = `${marker} Other`
    for (const title of [matchingTitle, otherTitle]) {
      await page.getByRole("button", { name: "Add Item" }).click()
      await page.getByLabel("Title", { exact: true }).fill(title)
      await page.getByRole("button", { name: "Save" }).click()
      await expect(page.getByRole("dialog")).not.toBeVisible()
      await expect(page.getByRole("cell", { name: title, exact: true })).toBeVisible()
    }

    const query = `${marker} alpha`
    const responsePromise = page.waitForResponse((response) => {
      const url = new URL(response.url())
      return url.pathname === "/api/v1/items/" && url.searchParams.get("q") === query
    })
    const search = page.getByRole("searchbox", { name: "Search items by title" })
    await search.fill(query)
    const response = await responsePromise
    expect(response.ok()).toBeTruthy()
    expect((await response.json()).count).toBe(1)
    await expect(page.getByRole("cell", { name: matchingTitle, exact: true })).toBeVisible()
    await expect(page.getByRole("cell", { name: otherTitle, exact: true })).not.toBeVisible()

    await search.fill(`${marker} missing`)
    await expect(page.getByText("No items match your search")).toBeVisible()
    await search.fill("")
    await expect(page.getByRole("cell", { name: matchingTitle, exact: true })).toBeVisible()
    await expect(page.getByRole("cell", { name: otherTitle, exact: true })).toBeVisible()
  })

  test("Cancel item creation", async ({ page }) => {
    await page.getByRole("button", { name: "Add Item" }).click()
    await page.getByLabel("Title").fill("Test Item")
    await page.getByRole("button", { name: "Cancel" }).click()

    await expect(page.getByRole("dialog")).not.toBeVisible()
  })

  test("Title is required", async ({ page }) => {
    await page.getByRole("button", { name: "Add Item" }).click()
    await page.getByLabel("Title").fill("")
    await page.getByLabel("Title").blur()

    await expect(page.getByText("Title is required")).toBeVisible()
  })

  test.describe("Edit and Delete", () => {
    let itemTitle: string

    test.beforeEach(async ({ page }) => {
      itemTitle = randomItemTitle()

      await page.getByRole("button", { name: "Add Item" }).click()
      await page.getByLabel("Title").fill(itemTitle)
      await page.getByRole("button", { name: "Save" }).click()
      await expect(page.getByText("Item created successfully")).toBeVisible()
      await expect(page.getByRole("dialog")).not.toBeVisible()
    })

    test("Edit an item successfully", async ({ page }) => {
      const itemRow = page.getByRole("row").filter({ hasText: itemTitle })
      await itemRow.getByRole("button").last().click()
      await page.getByRole("menuitem", { name: "Edit Item" }).click()

      const updatedTitle = randomItemTitle()
      await page.getByLabel("Title").fill(updatedTitle)
      await page.getByRole("button", { name: "Save" }).click()

      await expect(page.getByText("Item updated successfully")).toBeVisible()
      await expect(page.getByText(updatedTitle)).toBeVisible()
    })

    test("Delete an item successfully", async ({ page }) => {
      const itemRow = page.getByRole("row").filter({ hasText: itemTitle })
      await itemRow.getByRole("button").last().click()
      await page.getByRole("menuitem", { name: "Delete Item" }).click()

      await page.getByRole("button", { name: "Delete" }).click()

      await expect(
        page.getByText("The item was deleted successfully"),
      ).toBeVisible()
      await expect(page.getByText(itemTitle)).not.toBeVisible()
    })
  })
})

test.describe("Items empty state", () => {
  test.use({ storageState: { cookies: [], origins: [] } })

  test("Shows empty state message when no items exist", async ({ page }) => {
    const email = randomEmail()
    const password = randomPassword()
    await createUser({ email, password })
    await logInUser(page, email, password)

    await page.goto("/items")

    await expect(page.getByText("You don't have any items yet")).toBeVisible()
    await expect(page.getByText("Add a new item to get started")).toBeVisible()
  })
})
