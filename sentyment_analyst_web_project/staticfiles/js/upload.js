document.addEventListener("DOMContentLoaded", function () {
  // Manejo del input de archivo y label
  const fileInput = document.getElementById("file");
  const fileLabel = document.getElementById("file-label");
  const errorMsg = document.getElementById("error-msg");

  if (fileInput && fileLabel) {
    fileInput.addEventListener("change", function () {
      if (this.files.length > 0) {
        fileLabel.textContent = this.files[0].name;
        if (errorMsg) errorMsg.style.display = "none";
      } else {
        fileLabel.textContent = "Agrega un archivo excel o csv";
      }
    });
  }

  // Footer links dinámicos
  document.querySelectorAll(".footer-links a").forEach((link) => {
    console.log("Link: ", link);
    link.addEventListener("click", function (e) {
      e.preventDefault();
      const rightContent = document.querySelector(".right-content");
      if (this.textContent.includes("Ayuda")) {
        rightContent.innerHTML = `
          <h2>Ayuda</h2>
          <p>
            Uno de los problemas más frecuentes ocurre cuando el archivo cargado no contiene todas las columnas requeridas, lo que puede generar errores durante el procesamiento. Otro inconveniente común es subir archivos con encabezados mal escritos o modificados, especialmente en "Post Body", lo cual impide al modelo identificar el texto a analizar. Si el archivo tiene celdas vacías en esa columna, esas filas serán ignoradas. Además, si tu archivo supera el tamaño permitido por la plataforma (usualmente 10MB), es recomendable dividirlo en partes más pequeñas. Si experimentas lentitud, recuerda que el modelo de análisis corre en un servidor especializado: puede tardar algunos segundos dependiendo del tamaño del archivo y la carga del sistema. Ante cualquier inconveniente, recomendamos revisar bien los nombres de las columnas y asegurarte de que estás subiendo un archivo en el formato correcto (.csv o .xlsx).
          </p>
        `;
      } else if (this.textContent.includes("Recomendaciones")) {
        rightContent.innerHTML = `
          <h2>Recomendaciones</h2>
          <p>
            Para garantizar el funcionamiento óptimo del servicio, asegúrate de que tu archivo esté limpio y estructurado de acuerdo al formato requerido. Evita cargar textos muy extensos (más de 280 caracteres por fila), ya que pueden ser truncados o generar predicciones menos precisas. Si deseas utilizar esta herramienta en otro contexto por ejemplo, en el análisis de comentarios en encuestas, reseñas de productos o notas de prensa solo debes adaptar tus datos a la columna "Post Body" y replicar las demás columnas como vacías o genéricas. El modelo fue entrenado en español con datos reales de redes sociales, por lo que funciona mejor con texto informal, pero también se desempeña bien en registros más neutros. Finalmente, si deseas integrar esta herramienta en tu propio flujo de trabajo, puedes contactarnos para acceder a una API o servicio personalizado.
          </p>
        `;
      } else {
        // ¿Como empezar?
        rightContent.innerHTML = `
          <h2>¿Como empezar?</h2>
          <p>
            La plataforma de análisis de sentimiento fue diseñada como parte de un trabajo de tesis para proporcionar una solución eficiente, automatizada y confiable que permita a investigadores, periodistas y analistas interpretar rápidamente grandes volúmenes de datos sociales, en especial desde redes como Twitter. El sistema procesa archivos .csv o .xlsx que contengan publicaciones, identificando el sentimiento asociado a cada entrada como positivo, neutro o negativo. Para que la plataforma funcione correctamente, el archivo debe tener una estructura específica, siendo la columna "Post Body" (cuerpo del texto) la principal fuente de análisis. Una vez cargado, el sistema devuelve un panel visual (dashboard) con métricas clave como precisión del análisis, gráficos de distribución, y una opción para descargar resultados en PDF. Esto permite ahorrar tiempo y obtener insights inmediatos para estudios de opinión, campañas, o monitoreo de medios.
          </p>
          <table class="example-table">
            <tr>
              <th>Name</th>
              <th>Handle</th>
              <th>Retweets</th>
              <th>Likes</th>
              <th>Comments</th>
              <th>Views</th>
              <th>Post Body</th>
              <th>Timestamp</th>
              <th>Interacciones y Audiencia</th>
              <th>Periodo</th>
            </tr>
            <tr>
              <td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
            </tr>
          </table>
          <div class="note">
            <span>⚠️</span>
            <span>
              Nota: Aunque todas las columnas deben estar presentes, solo "Post Body" es usada para el análisis de sentimiento.<br>
              Las demás columnas son utilizadas para enriquecer el dashboard o exportar el resultado completo.
            </span>
          </div>
        `;
      }
    });
  });
  // Manejo del submit del formulario
  const uploadForm = document.querySelector(".upload-form");
  if (uploadForm) {
    uploadForm.addEventListener("submit", function (e) {
      e.preventDefault();

      // Mostrar animación de procesando en el right-panel
      const rightContent = document.querySelector(".right-content");
      rightContent.innerHTML = `
        <div class="processing-animation">
          <div class="spinner"></div>
          <p>Procesando datos...</p>
        </div>
      `;

      const formData = new FormData(this);

      fetch(uploadForm.action, {
        method: "POST",
        headers: {
          "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
            .value,
        },
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.error) {
            rightContent.innerHTML = `<p style="color:red;">${data.error}</p>`;
            return;
          }

          // Renderiza el dashboard dinámicamente usando data
          rightContent.innerHTML = renderDashboard(data.data);

          // Llama a tu función de gráficos con los datos recibidos
          window.renderDashboardCharts(
            data.data.sentiment_counts || {},
            data.data.sentiment_month || [],
            data.data.sentimiento_tipo_cuenta || {}
          );

          // --- Nube de palabras: asegúrate de que esto esté dentro del .then ---
          let topWords = Array.isArray(data.data.top_words) ? [...data.data.top_words] : [];
          if (topWords.length > 0) {
            // Calcula el máximo valor de frecuencia para escalar el tamaño
            const maxCount = Math.max(...topWords.map(w => w[1]));
            // Usa weightFactor como función para escalar el tamaño de la palabra
            WordCloud(document.getElementById('wordCloud'), {
              list: topWords,
              gridSize: 10,
              weightFactor: function (size) {
                // Escala el tamaño entre 14 y 48 px según la frecuencia
                return 14 + (size / maxCount) * 34;
              },
              fontFamily: 'Arial',
              color: '#ff9800',
              backgroundColor: '#fff',
              rotateRatio: 0,
              minSize: 12,
              drawOutOfBound: false
            });
          }
        })
        .catch(() => {
          rightContent.innerHTML = "<p>Error al cargar el resultado.</p>";
        });
    });
  }
});
// --- Código de dashboard-plotly.js ---
window.renderDashboardCharts = function (sentimentCounts, sentimentMonth, sentimientoTipoCuenta) {
  console.log("renderDashboardCharts called");
  console.log("sentimentCounts:", sentimentCounts);
  console.log("sentimentMonth:", sentimentMonth);

  // Pie chart
  Plotly.newPlot(
    "sentimentPie",
    [
      {
        values: Object.values(sentimentCounts),
        labels: Object.keys(sentimentCounts),
        type: "pie",
        marker: { colors: ["#ff9800", "#ffb74d", "#ffe0b2"] }, // escala de naranjas
      },
    ],
    {
      legend: { orientation: "h" },
      margin: { t: 30, b: 30, l: 0, r: 0 },
      height: 400,
      width: 400,
    },
    { responsive: true }
  );

  // Line chart
  if (sentimentMonth && sentimentMonth.length > 0) {
    const meses = [...new Set(sentimentMonth.map((item) => item.YearMonth))];
    const sentimientos = [
      ...new Set(sentimentMonth.map((item) => item.Sentimiento)),
    ];
    const colors = {
      positivo: "#ff9800", // Naranja fuerte
      negativo: "#ff5722", // Naranja rojizo oscuro
      neutro: "#ffd54f", // Naranja claro/amarillo
    };
    const data = sentimientos.map((sent) => ({
      x: meses,
      y: meses.map((mes) => {
        const found = sentimentMonth.find(
          (item) => item.YearMonth === mes && item.Sentimiento === sent
        );
        return found ? found.Conteo : 0;
      }),
      mode: "lines+markers",
      name: sent.charAt(0).toUpperCase() + sent.slice(1),
      line: { color: colors[sent] || "#ff9800", width: 3 },
      marker: { size: 8 },
    }));
    Plotly.newPlot(
      "sentimentLine",
      data,
      {
        xaxis: { title: "Mes y Año" },
        yaxis: { title: "Cantidad de Posts", rangemode: "tozero" },
        legend: { orientation: "h" },
        margin: { t: 30, b: 40, l: 40, r: 10 },
        height: 500,
        width: 1400,
      },
      { responsive: true }
    );
  }

  // Stacked Bar Chart de Sentimiento por Tipo de Cuenta
  if (sentimientoTipoCuenta && Object.keys(sentimientoTipoCuenta).length > 0) {
    const tipos = Object.keys(sentimientoTipoCuenta);
    const sentimientos = ["positivo", "negativo", "neutro"];
    const colors = {
      positivo: "#ff9800",
      negativo: "#ff5722",
      neutro: "#ffd54f"
    };

    const traces = sentimientos.map(sent => ({
      y: tipos, // Eje Y ahora son los tipos de cuenta
      x: tipos.map(tipo => sentimientoTipoCuenta[tipo]?.[sent] || 0),
      name: sent.charAt(0).toUpperCase() + sent.slice(1),
      type: 'bar',
      orientation: 'h', // <-- barras horizontales
      marker: { color: colors[sent] }
    }));

    Plotly.newPlot('sentimentByTypeBar', traces, {
      barmode: 'stack',
      xaxis: { title: 'Cantidad de Posts', rangemode: 'tozero' },
      legend: { orientation: 'h' },
      margin: { t: 30, b: 40, l: 80, r: 10 },
      height: 250,
      width: 400
    }, { responsive: true });
  }
  
};

function renderDashboard(data) {
  return `
    <div class="parent">
      <div class="div1 card">
        <div>
          <h3>Top 10 Usuarios<br />por Interacciones y Audiencia</h3>
          <ul>
            ${(data.top_users || [])
              .map(
                (user) => `
              <li>
                <span>
                  <span class="user-handle">${user.Name}</span>
                  <span style="color: #888">(${user.Handle})</span>
                </span>
                <span class="user-score">
                  ${user["Interacciones y Audiencia"]}
                </span>
              </li>
            `
              )
              .join("")}
          </ul>
        </div>
      </div>
      <div class="div2 card">
        <h3>Estadísticas Generales</h3>
        <div class="stats-columns">
          <ul class="stats-list">
            <li>
              <i class="fa-solid fa-retweet stats-icon"></i>
              <div>
                <strong>Total Retweets:</strong><br />
                ${data.total_retweets}
              </div>
            </li>
            <li>
              <i class="fa-solid fa-heart stats-icon"></i>
              <div>
                <strong>Total Likes:</strong><br />
                ${data.total_likes}
              </div>
            </li>
            <li>
              <i class="fa-solid fa-eye stats-icon"></i>
              <div>
                <strong>Total Views:</strong><br />
                ${data.total_views}
              </div>
            </li>
            <li>
              <i class="fa-solid fa-comments stats-icon"></i>
              <div>
                <strong>Total Comments:</strong><br />
                ${data.total_comments}
              </div>
            </li>
          </ul>
          <ul class="stats-list">
            <li>
              <i class="fa-solid fa-landmark stats-icon"></i>
              <div>
                <strong>Institucionales:</strong><br />
                ${data.conteo_tipo_cuenta?.Institucionales ?? 0}
              </div>
            </li>
            <li>
              <i class="fa-solid fa-bullhorn stats-icon"></i>
              <div>
                <strong>Medios de Comunicación:</strong><br />
                ${data.conteo_tipo_cuenta?.["Medios de Comunicación"] ?? 0}
              </div>
            </li>
            <li>
              <i class="fa-solid fa-users stats-icon"></i>
              <div>
                <strong>General:</strong><br />
                ${data.conteo_tipo_cuenta?.General ?? 0}
              </div>
            </li>
            <li>
              <i class="fa-solid fa-robot stats-icon"></i>
              <div>
                <strong>Bots:</strong><br />
                ${data.conteo_tipo_cuenta?.Bots ?? 0}
              </div>
            </li>
          </ul>
        </div>
      </div>
      <div class="div7 card">
        <h3>Sentimiento por Tipo de Cuenta</h3>
        <div class="canvas-wrapper">
          <div id="sentimentByTypeBar"></div>
        </div>
      </div>
      <div class="div3 card">
        <div>
          <h3>Distribución de Sentimientos</h3>
          <div class="canvas-wrapper">
            <div id="sentimentPie"></div>
          </div>
        </div>
      </div>
      <div class="div4-row" style="display: flex; gap: 1.5rem;">
        <div class="div4 card" style="flex:1;">
          ${
            data.post_max_interacciones
              ? `
            <div>
              <h3>Post con más Interacciones y Audiencia</h3>
              <ul>
                <li>
                  <strong>Nombre:</strong>
                  <span style="color: #34495e; font-size: 1.2em">
                    ${data.post_max_interacciones.Name}
                  </span>
                </li>
                <li>
                  <strong>Usuario:</strong>
                  <span style="color:rgb(255, 153, 0); font-size: 1.1em">
                    ${data.post_max_interacciones.Handle}
                  </span>
                </li>
                <li>
                  <strong>Retweets:</strong> ${data.post_max_interacciones.Retweets}
                </li>
                <li><strong>Likes:</strong> ${data.post_max_interacciones.Likes}</li>
                <li>
                  <strong>Comments:</strong> ${data.post_max_interacciones.Comments}
                </li>
                <li><strong>Views:</strong> ${data.post_max_interacciones.Views}</li>
                <li>
                  <strong>Post:</strong>
                  ${data.post_max_interacciones["Post Body"]}
                </li>
                <li>
                  <strong>Fecha:</strong>
                  ${data.post_max_interacciones.Timestamp}
                </li>
                <li>
                  <strong>Sentimiento:</strong>
                  ${data.post_max_interacciones.Sentimiento}
                </li>
              </ul>
            </div>
            `
              : ""
          }
        </div>
      </div>
      <div class="div6 card">
        <div class="canvas-wrapper">
          <h3>Sentimientos por Mes</h3>
          <div id="sentimentLine"></div>
        </div>
      </div>
      <div class="div8 card">
        <h3>Palabras más frecuentes</h3>
        <div id="wordCloud" style="width:100%;height:250px;"></div>
      </div>
    </div>
  `;
}
