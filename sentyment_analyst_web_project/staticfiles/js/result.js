// console.log("result.js loaded Hola");
// window.renderDashboardCharts = function(sentimentCounts, sentimentMonth) {
//   console.log("renderDashboardCharts called");
//   console.log("sentimentCounts:", sentimentCounts);
//   console.log("sentimentMonth:", sentimentMonth);

//   // Pie chart
//   if (sentimentCounts && Object.keys(sentimentCounts).length > 0) {
//     Plotly.newPlot('sentimentPie', [{
//       values: Object.values(sentimentCounts),
//       labels: Object.keys(sentimentCounts),
//       type: 'pie',
//       marker: { colors: ['#4caf50', '#f44336', '#ffeb3b'] }
//     }], {
//       legend: { orientation: "h" },
//       margin: { t: 30, b: 30, l: 0, r: 0 }
//     }, { responsive: true });
//   }

//   // Line chart
//   if (sentimentMonth && sentimentMonth.length > 0) {
//     const meses = [...new Set(sentimentMonth.map(item => item.YearMonth))];
//     const sentimientos = [...new Set(sentimentMonth.map(item => item.Sentimiento))];
//     const colors = { positivo: "#4caf50", negativo: "#f44336", neutro: "#ffeb3b" };
//     const data = sentimientos.map(sent => ({
//       x: meses,
//       y: meses.map(mes => {
//         const found = sentimentMonth.find(item => item.YearMonth === mes && item.Sentimiento === sent);
//         return found ? found.Conteo : 0;
//       }),
//       mode: 'lines+markers',
//       name: sent.charAt(0).toUpperCase() + sent.slice(1),
//       line: { color: colors[sent] || "#888", width: 3 },
//       marker: { size: 8 }
//     }));
//     Plotly.newPlot('sentimentLine', data, {
//       xaxis: { title: 'Mes y Año' },
//       yaxis: { title: 'Cantidad de Posts', rangemode: 'tozero' },
//       legend: { orientation: "h" },
//       margin: { t: 30, b: 40, l: 40, r: 10 }
//     }, { responsive: true });
//   }
// };