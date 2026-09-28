import type { CrateFoldHandle, CrateRecord } from "./crate-fold";

/** How much darker than the crate an item is. 0.70. */
export const DARKER: number;
/** Where the tabs sit, in order, repeating. */
export const TABS: number[];
export const ITEM_W: number;
export const ITEM_H: number;

/** The crate's colour, darker by a share of itself. */
export function deepen(hex: string, by?: number): string;

/** Draw one item. Returns what setRecords() takes. */
export function drawItem(options: {
  /** The crate's colour, as "#rrggbb" */
  crate: string;
  /** Its place in the crate, which decides where its tab sits */
  index: number;
  /** The crate it is for */
  fold: Pick<CrateFoldHandle, "tabHeight" | "tabWidth" | "tabRun">;
  /** How much darker than the crate. Default 0.70 */
  darker?: number;
  style?: "moulded" | "plain";
  cut?: "folder" | "card";
}): CrateRecord;
