  // Get elements for availability filter
  const availabilityCheckboxes = document.querySelectorAll('#FilterInStock, #FilterPreOrder, #FilterOutOfStock');
  const availabilityCount = document.getElementById('availability-count');
  const availabilityReset = document.getElementById('availability-reset');

  // Update selected count for availability filter
  function updateAvailabilityCount() {
    const selectedCount = [...availabilityCheckboxes].filter(checkbox => checkbox.checked).length;
    availabilityCount.textContent = `${selectedCount} Selected`;
  }

  // Event listener for availability checkboxes
  availabilityCheckboxes.forEach(checkbox => {
    checkbox.addEventListener('change', updateAvailabilityCount);
  });

  // Reset functionality for availability filter
  availabilityReset.addEventListener('click', () => {
    availabilityCheckboxes.forEach(checkbox => checkbox.checked = false);
    updateAvailabilityCount();
  });
