function ExerciseCard({ title, description }) {
  return (
    <div className="exerciseCard">
      <div className="cardImage"></div>

      <div className="cardContent">
        <h3>{title}</h3>
        <p>{description}</p>
        <button>둘러보기 →</button>
      </div>
    </div>
  );
}

export default ExerciseCard;