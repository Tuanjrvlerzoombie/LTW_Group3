// Tab functionality for profile page
document.addEventListener("DOMContentLoaded", function () {
  // Change View functionality for Home page
  const changeViewBtn = document.getElementById("changeViewBtn");
  const tableView = document.getElementById("tableView");
  const gridView = document.getElementById("gridView");

  if (changeViewBtn) {
    changeViewBtn.addEventListener("click", function () {
      if (tableView.style.display === "none") {
        tableView.style.display = "block";
        gridView.style.display = "none";
        changeViewBtn.classList.remove("active");
      } else {
        tableView.style.display = "none";
        gridView.style.display = "block";
        changeViewBtn.classList.add("active");
      }
    });
  }

  // Profile page tab functionality
  const myArticlesTab = document.getElementById("myArticlesTab");
  const accountSettingsTab = document.getElementById("accountSettingsTab");
  const recentActivityTab = document.getElementById("recentActivityTab");

  const myArticlesContent = document.getElementById("myArticlesContent");
  const accountSettingsContent = document.getElementById(
    "accountSettingsContent"
  );
  const recentActivityContent = document.getElementById(
    "recentActivityContent"
  );

  if (myArticlesTab && accountSettingsTab && recentActivityTab) {
    // Set default active tab
    myArticlesTab.classList.add("active");

    myArticlesTab.addEventListener("click", function () {
      // Update tab buttons
      myArticlesTab.classList.add("active");
      accountSettingsTab.classList.remove("active");
      recentActivityTab.classList.remove("active");

      // Update content visibility
      myArticlesContent.style.display = "block";
      accountSettingsContent.style.display = "none";
      recentActivityContent.style.display = "none";
    });

    accountSettingsTab.addEventListener("click", function () {
      // Update tab buttons
      myArticlesTab.classList.remove("active");
      accountSettingsTab.classList.add("active");
      recentActivityTab.classList.remove("active");

      // Update content visibility
      myArticlesContent.style.display = "none";
      accountSettingsContent.style.display = "block";
      recentActivityContent.style.display = "none";
    });

    recentActivityTab.addEventListener("click", function () {
      // Update tab buttons
      myArticlesTab.classList.remove("active");
      accountSettingsTab.classList.remove("active");
      recentActivityTab.classList.add("active");

      // Update content visibility
      myArticlesContent.style.display = "none";
      accountSettingsContent.style.display = "none";
      recentActivityContent.style.display = "block";
    });
  }
});
