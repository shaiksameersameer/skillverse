const data = {
  labels: ["Matched Skills", "Unmatched Skills"],
  datasets: [{
    data: [commonCount, totalCount - commonCount],
    backgroundColor: ["#34D399", "#EF4444"],
    borderColor: "#111827"
  }]
};

const config = {
  type: "pie",
  data: data,
  options: {
    animation: {
      animateScale: true,
      animateRotate: true
    },
    responsive: true,
    maintainAspectRatio: false
  }
};

new Chart(document.getElementById("matchChart"), config);
