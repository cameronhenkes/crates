export type CrateFoldState = "closed" | "folding" | "folded" | "unfolding";

export type CrateFoldTextures = {
  "front.png": string;
  "back.png": string;
  "side.png": string;
  "floor.png": string;
};

export type CrateFoldOptions = {
  /** The three module: `await import("three")` */
  THREE: typeof import("three");
  /** Element the canvas is appended to */
  mount: HTMLElement;
  textures: CrateFoldTextures;
  /** Drawing size in CSS pixels. The canvas itself scales to its container. */
  size?: number;
  onState?: (state: CrateFoldState) => void;
  onReady?: () => void;
};

export type CrateFoldHandle = {
  /** Fold or unfold. Returns true when it is now folding. */
  toggle(): boolean;
  /** Jump to a position, 0 closed to 1 folded, without animating. */
  set(position: number): void;
  dispose(): void;
  /** Length of the fold in milliseconds */
  duration: number;
};

export function createCrateFold(options: CrateFoldOptions): CrateFoldHandle;
