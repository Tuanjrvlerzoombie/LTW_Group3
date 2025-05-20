document.addEventListener("DOMContentLoaded", function () {
  const startDateInput = document.getElementById("start_day");
  const endDateInput = document.getElementById("end_day");

  const startDatePicker = flatpickr(startDateInput, {
    dateFormat: "d-M-Y",
    allowInput: false,
    onChange: function (selectedDates) {
      if (selectedDates[0]) {
        endDatePicker.set("minDate", selectedDates[0]);
      }
    },
    onClose: function () {
      startDateInput.focus();
    }
  });

  const endDatePicker = flatpickr(endDateInput, {
    dateFormat: "d-M-Y",
    allowInput: false,
    onChange: function (selectedDates) {
      if (selectedDates[0]) {
        startDatePicker.set("maxDate", selectedDates[0]);
      }
    },
    onClose: function () {
      endDateInput.focus();
    }
  });

  // Mở flatpickr khi click icon
  document.querySelectorAll('.fas.fa-calendar').forEach(function (icon) {
    icon.addEventListener('mousedown', function (event) {
      event.preventDefault();
      const input = this.parentElement.querySelector('input');
      input._flatpickr.open();
    });
  });

  const searchForm = document.querySelector('.search-form');
  const searchInput = document.querySelector('.search-input');
  const categorySelect = document.getElementById('category');

  if (searchForm) {
    searchForm.addEventListener('submit', function (event) {
      event.preventDefault();
      const query = searchInput?.value.trim() || "";
      if (query) {
        window.location.href = `/search/?search=${encodeURIComponent(query)}`;
      } else {
        filterArticles(); // Chỉ lọc khi form được gửi
      }
    });
  }

  if (searchInput) {
    searchInput.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        searchInput.value = searchInput.value.trim();
        if (searchForm) searchForm.submit();
      }
    });
  }

  // Load dữ liệu từ URL chỉ khi form đã được gửi
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has("search") && searchInput) {
    searchInput.value = decodeURIComponent(urlParams.get("search"));
  }
  if (urlParams.has("category") && categorySelect) {
    categorySelect.value = decodeURIComponent(urlParams.get("category"));
  }
  if (urlParams.has("start_day") && startDateInput) {
    startDateInput.value = decodeURIComponent(urlParams.get("start_day"));
  }
  if (urlParams.has("end_day") && endDateInput) {
    endDateInput.value = decodeURIComponent(urlParams.get("end_day"));
  }

  // Chỉ lọc khi có tham số form_submitted=1
  if (urlParams.has("form_submitted") && urlParams.get("form_submitted") === "1") {
    filterArticles();
  }
});

// ======== FUNCTION ========

function parseDate(dateStr) {
  if (!dateStr) return null;
  try {
    const parts = dateStr.split(/[-/]/);
    const months = {
      Jan: 0, Feb: 1, Mar: 2, Apr: 3, May: 4, Jun: 5,
      Jul: 6, Aug: 7, Sep: 8, Oct: 9, Nov: 10, Dec: 11
    };
    let day, month, year;
    if (isNaN(parts[1])) {
      day = parseInt(parts[0], 10);
      month = months[parts[1].substring(0, 3)];
      year = parseInt(parts[2], 10);
    } else {
      year = parseInt(parts[0], 10);
      month = parseInt(parts[1], 10) - 1;
      day = parseInt(parts[2], 10);
    }
    const date = new Date(year, month, day);
    return isNaN(date.getTime()) ? null : date;
  } catch (error) {
    console.error("Date parsing error:", error);
    return null;
  }
}

function filterArticles() {
  const articles = document.querySelectorAll(".featured-article, .article-card");
  if (!articles.length) return;

  const searchInput = document.querySelector(".search-input");
  const categorySelect = document.getElementById("category");
  const startDateInput = document.getElementById("start_day");
  const endDateInput = document.getElementById("end_day");

  const searchTerm = searchInput?.value.trim().toLowerCase() || "";
  const selectedCategory = categorySelect?.value.toLowerCase() || "";
  const startDateStr = startDateInput?.value || "";
  const endDateStr = endDateInput?.value || "";

  const startDate = startDateStr ? parseDate(startDateStr) : null;
  const endDate = endDateStr ? parseDate(endDateStr) : null;

  if (startDate) startDate.setHours(0, 0, 0, 0);
  if (endDate) endDate.setHours(23, 59, 59, 999);

  let hasResults = false;

  articles.forEach(article => {
    const title = article.querySelector("h2, h3")?.textContent?.toLowerCase() || "";
    const content = article.querySelector(".article-summary")?.textContent?.toLowerCase() || "";
    const author = article.querySelector(".author")?.textContent?.replace("Author:", "").trim().toLowerCase() || "";
    const dateStr = article.querySelector(".date")?.textContent.split("(")[0].trim() || "";
    const articleDate = parseDate(dateStr);
    const articleCategory = article.dataset.category?.toLowerCase() || "";

    const matchesSearch = !searchTerm ||
      title.includes(searchTerm) ||
      content.includes(searchTerm) ||
      author.includes(searchTerm);

    const matchesCategory = !selectedCategory ||
      selectedCategory === "all categories" ||
      articleCategory === selectedCategory;

    const matchesDate = (!startDate || (articleDate && articleDate >= startDate)) &&
      (!endDate || (articleDate && articleDate <= endDate));

    const isVisible = matchesSearch && matchesCategory && matchesDate;
    article.style.display = isVisible ? "" : "none";
    if (isVisible) hasResults = true;
  });

  const noResultsMsg = document.querySelector(".no-articles");
  if (noResultsMsg) {
    noResultsMsg.style.display = hasResults ? "none" : "block";
    noResultsMsg.textContent = hasResults ? "" : `No matching articles found${searchTerm ? ` for "${searchTerm}"` : ""}`;
  }

  updateSearchURL(searchTerm, selectedCategory, startDateStr, endDateStr);
}

function updateSearchURL(searchTerm, category, startDate, endDate) {
  const url = new URL(window.location);
  url.searchParams.set("search", searchTerm || "");
  category && category !== "all categories" ?
    url.searchParams.set("category", category) :
    url.searchParams.delete("category");
  startDate ? url.searchParams.set("start_day", startDate) : url.searchParams.delete("start_day");
  endDate ? url.searchParams.set("end_day", endDate) : url.searchParams.delete("end_day");
  window.history.pushState({}, "", url);
}

function debounce(func, delay) {
  let timeout;
  return function () {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, arguments), delay);
  };
}