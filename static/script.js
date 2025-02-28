document.getElementById("search_button").addEventListener("click", function() {
    let query = document.getElementById("search_input").value.trim();

    if (query) {
        fetch(`/search?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            let results = document.getElementById("search_results");
            results.innerHTML = "";
            
            if (data.length === 0) {
                resultsDiv.innerHTML = "<p>No results found.</p>";
            }else {
            data.forEach(result => {
                let item = document.createElement("p");
                item.textContent = `Name: ${product.name}, Brand: ${product.brand}, Price: ${product.dp}`;
                results.appendChild(item);
            });
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
    }
});

document.getElementById("toggleFormButton").addEventListener("click", function(event) { 
    let form = document.getElementById("addProductForm");
    form.classList.toggle("active");
});

// Toggle Mobile Menu
const mobileMenu = document.getElementById("mobileMenu");
const navbarMenu = document.getElementById("navbarMenu");

mobileMenu.addEventListener("click", ( )=> {
    mobileMenu.classList.toggle("active");
    navbarMenu.classList.toggle("active");
});


// Search Feature
document.addEventListener("DOMContentLoaded", function() {
    const searchIcon = document.getElementById("searchIcon");
    const searchContainer = document.getElementById("searchContainer");

    searchIcon.addEventListener("click", function() {
        searchContainer.classList.toggle("hidden");
    });
});

// Ensure DOM is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');

    // Toggle visibility of the search form
    window.toggleSearch = function () {
        if (searchForm.style.display === 'none' || searchForm.style.display === '') {
            searchForm.style.display = 'block';
            searchInput.focus(); // Auto-focus when input appears
        } else {
            searchForm.style.display = 'none';
        }
    };
});

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("productForm");
  
    form.addEventListener("submit", (event) => {
      const inputs = form.querySelectorAll("input[required]");
      let isValid = true;
  
      inputs.forEach((input) => {
        if (!input.value.trim()) {
          isValid = false;
        }
      });
  
      if (!isValid) {
        event.preventDefault();
        alert("Please fill all fields before submitting.");
      }
    });
  });
  