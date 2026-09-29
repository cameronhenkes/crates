"use client";

import { useState } from "react";
import styles from "./CrateFold.module.css";

type Props = {
  /** Path to a crate SVG, e.g. "/images/crates/rust.svg" */
  src: string;
  /** Colour name, used in the label and the accessible name */
  name?: string;
  /** Rendered beneath the crate. Motion is never the only feedback channel. */
  showLabel?: boolean;
  className?: string;
};

/**
 * A crate that folds flat when you click it.
 *
 * The animation is doing a job, not decorating: hovering says "this responds",
 * and clicking demonstrates the one thing about the object you cannot see in a
 * still image -- that it folds. If you drop the label, keep some other static
 * cue for the state.
 */
export function CrateFold({ src, name = "crate", showLabel = true, className }: Props) {
  const [folded, setFolded] = useState(false);

  return (
    <div className={className}>
      <button
        type="button"
        aria-pressed={folded}
        aria-label={`${name} crate, ${folded ? "folded flat" : "assembled"}. Activate to ${folded ? "unfold" : "fold flat"}.`}
        className={`${styles.button} ${folded ? styles.folded : ""}`}
        onClick={() => setFolded((f) => !f)}
      >
        <span className={styles.lift}>
          <span className={styles.fold}>
            <img className={styles.img} src={src} alt="" aria-hidden="true" />
          </span>
        </span>
      </button>

      {showLabel && (
        <p aria-hidden="true">
          Crate is <b>{folded ? "folded flat" : "assembled"}</b>
          {" · "}
          {folded ? "click to unfold" : "click to fold flat"}
        </p>
      )}
    </div>
  );
}

export default CrateFold;
