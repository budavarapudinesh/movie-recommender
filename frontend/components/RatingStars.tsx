"use client";

import { useState } from "react";

export default function RatingStars({
  value = 0,
  onChange,
  readonly = false,
}: {
  value?: number;
  onChange?: (rating: number) => void;
  readonly?: boolean;
}) {
  const [hover, setHover] = useState(0);

  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          disabled={readonly}
          className={`text-2xl transition ${
            readonly ? "cursor-default" : "cursor-pointer hover:scale-110"
          } ${(hover || value) >= star ? "text-amber-400" : "text-gray-600"}`}
          onClick={() => onChange?.(star)}
          onMouseEnter={() => !readonly && setHover(star)}
          onMouseLeave={() => !readonly && setHover(0)}
        >
          ★
        </button>
      ))}
      {value > 0 && <span className="text-gray-400 text-sm ml-2 self-center">{value}/5</span>}
    </div>
  );
}
