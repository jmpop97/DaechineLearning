// window.onload = () => {
//     console.log("로딩");
// }

// 카테고리 가져오기
async function getCategoryList() {
    const response = await fetch('http://127.0.0.1:8080/articles/genre/');
    const data = await response.json();

    return data;
}

//카테고리 선택 옵션
async function createCategoryOptions() {
    const categories = await getCategoryList();
    const selectElement = document.getElementById("category");

    for (let i = 0; i < categories.length; i++) {
        const optionElement = document.createElement("option");
        optionElement.value = categories[i].id;
        optionElement.textContent = categories[i].name;
        selectElement.appendChild(optionElement);
    }
}

createCategoryOptions();

//등록
async function handleProductCreate() {
    console.log("등록");

    const access = localStorage.getItem("access");
    const title = document.getElementById("title").value;
    const content = document.getElementById("content").value;
    const image = document.getElementById("image").file;
    const media = document.getElementById("media").file;
    const sound = document.getElementById("sound").file;
    const category = Array.from(
        document.getElementById("category").selectedOptions
    ).map((option) => option.value);

    const formData = new FormData();
    formData.append("title", title);
    formData.append("content", content);
    formData.append("image", image);
    formData.append("media", media);
    formData.append("sound", sound);
    category.forEach((category_id) => formData.append("category", category_id));
    
    console.log(formData.getAll);

    const response = await fetch("http://127.0.0.1:8080/articles/", {
        headers: {
            Authorization: `Bearer ${access}`,
        },
        method: "POST",
        body: formData,
    });
    const data = await response.json();
    console.log(data);

    if (response.status == 200) {
        if (confirm("등록 완료!\n계속 등록 하시겠습니까?")) {
            return false;
        } else {
            window.location.href = "index.html";
        }
    } else {
        alert("잘못 된 요청입니다.");
    }
}

// 자식창 열기
function musicSearch() {
    window.open(`/templates/music_search.html`, "name", "width=800, height=600, top=50, left=50")
}

// // 자식창
// let openWin = window.open("Child.html");
// openWin.document.getElementById("cInput").value = "전달하고자 하는 값";


