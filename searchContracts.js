const searchContracts = async () => {
  const API_URL = 'https://api.topstepx.com/api/Contract/search';
  const AUTH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1laWRlbnRpZmllciI6IjEyMjcxMyIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL3NpZCI6ImU4NGJjY2E1LTdiOTItNGY5Ni1iMWMzLWFkMTM2ZWVhMmYzNCIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL25hbWUiOiJxdWFudHNhdnZpIiwiaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS93cy8yMDA4LzA2L2lkZW50aXR5L2NsYWltcy9yb2xlIjoidXNlciIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvYXV0aGVudGljYXRpb25tZXRob2QiOiJhcGkta2V5IiwibXNkIjpbIkNNRUdST1VQX1RPQiIsIkNNRV9UT0IiXSwibWZhIjoidmVyaWZpZWQiLCJleHAiOjE3NTI4NDg3MDJ9.duo2TvR5CwT3W9XLvqcJofg54x8V5-fZKbwb8UA5DrI' // Your full JWT token

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'accept': 'text/plain',
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${AUTH_TOKEN}`  // Attach the token
      },
      body: JSON.stringify({
        live: false,
        searchText: "NQ"
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json(); // or response.text() if API returns plain text
    console.log('Search results:', data);
    return data;
  } catch (error) {
    console.error('Failed to search contracts:', error);
    throw error;
  }
};

// Execute
searchContracts();

