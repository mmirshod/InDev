const inputFile = document.querySelector('#file');
const newImageArea = document.querySelector('#newImage')

inputFile.addEventListener('change', (event) => {
    const image = event.target.files[0];
    const reader = new FileReader();

    reader.onload = () => {
        const allImages = newImageArea.querySelectorAll('img');
        allImages.forEach(item => item.remove());

        const imgUrl = reader.result;
        const img = document.createElement('img');

        img.src = imgUrl;
        img.setAttribute('height', 200);
        img.setAttribute('width', 200);
        img.setAttribute('alt', 'new-img');

        newImageArea.appendChild(img);
    }
    reader.readAsDataURL(image)
})
