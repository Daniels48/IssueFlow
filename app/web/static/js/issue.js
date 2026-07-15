// connectWebSocket();
//
//
// window.onload = async () => {
//
//     const params = new URLSearchParams(
//         window.location.search,
//     );
//
//     const id = params.get("id");
//
//     const issue = await api(
//         `/issues/${id}`,
//     );
//
//     document.getElementById("title").innerText =
//         issue.title;
//
//     document.getElementById("description").innerText =
//         issue.description;
//
// };