import "./StarRating.css";

function StarRating({ value, onChange, readOnly = false }) {
  const stars = [1, 2, 3, 4, 5];

  return (
    <div className={`star-rating ${readOnly ? "star-rating-readonly" : ""}`}>
      {stars.map((star) => (
        <span
          key={star}
          className={star <= value ? "star star-filled" : "star"}
          onClick={() => !readOnly && onChange && onChange(star)}
        >
          ★
        </span>
      ))}
    </div>
  );
}

export default StarRating;