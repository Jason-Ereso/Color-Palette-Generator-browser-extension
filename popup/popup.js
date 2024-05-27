document.getElementById('generatePaletteName').addEventListener('click', () => {
    const name = document.getElementById('colorName').value;
    generatePaletteFromName(name);
});

document.getElementById('generatePaletteHex').addEventListener('click', () => {
    const hex = document.getElementById('hexColor').value;
    generatePaletteFromHex(hex);
});

document.getElementById('generatePaletteRGB').addEventListener('click', () => {
    const rgb = document.getElementById('rgbColor').value;
    generatePaletteFromRGB(rgb);
});

// function displayPalette(data) {
//     const paletteDiv = document.getElementById('palette');
//     paletteDiv.innerHTML = '';

//     const colorTypes = ['original', 'complementary', 'analogous', 'triadic', 'tetradic', 'monochromatic'];
//     colorTypes.forEach(type => {
//         const colors = Array.isArray(data[type][0]) ? data[type] : [data[type]];
//         colors.forEach(color => {
//             const colorSwatch = document.createElement('div');
//             colorSwatch.className = 'color-swatch';
//             colorSwatch.style.backgroundColor = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
//             paletteDiv.appendChild(colorSwatch);
//         });
//     });
// }

function displayPalette(data) {
    const paletteDiv = document.getElementById('palette');
    paletteDiv.innerHTML = '';

    const colorTypes = ['original', 'complementary', 'analogous', 'triadic', 'tetradic', 'monochromatic'];
    colorTypes.forEach(type => {
        const colors = Array.isArray(data[type][0]) ? data[type] : [data[type]];
        colors.forEach(color => {
            const colorSwatch = document.createElement('div');
            colorSwatch.className = 'color-swatch';
            const rgbColor = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
            const hexColor = rgbToHex(color[0], color[1], color[2]);
            colorSwatch.style.backgroundColor = rgbColor;
            colorSwatch.textContent = hexColor; // Display hex value inside color swatch
            paletteDiv.appendChild(colorSwatch);
        });
    });
}

function rgbToHex(r, g, b) {
    return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

// Function to copy text to clipboard
// function copyToClipboard(text) {
//     const textarea = document.createElement('textarea');
//     textarea.value = text;
//     document.body.appendChild(textarea);
//     textarea.select();
//     document.execCommand('copy');
//     document.body.removeChild(textarea);
// }

function copyToClipboard(text) {
    navigator.clipboard.writeText(text)
        .then(() => {
            console.log('Text copied to clipboard:', text);
            alert('Copied to clipboard: ' + text);
        })
        .catch(err => {
            console.error('Error copying text to clipboard:', err);
            alert('Failed to copy to clipboard. Please try again.');
        });
}

// Function to handle click on color swatch
function handleColorSwatchClick(rgbColor, hexColor) {
    copyToClipboard(rgbColor + ' ' + hexColor);
    alert(`Copied: ${rgbColor} ${hexColor}`);
}

// Add event listeners to color swatch elements
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.color-swatch').forEach(colorSwatch => {
        colorSwatch.addEventListener('click', function() {
            const rgbColor = this.getAttribute('data-rgb');
            const hexColor = this.getAttribute('data-hex');
            handleColorSwatchClick(rgbColor, hexColor);
        });
    });
});


document.getElementById('colorName').addEventListener('input', function() {
    updateCount(this);
});

function updateCount(input) {
    var count = input.value.length;
    document.getElementById('count').textContent = count + "/25";
}

async function generatePaletteFromName(name) {
    try {
        const response = await fetch('http://127.0.0.1:5000/predict', {  // Change the URL if deployed on a remote server
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name })
        });
        const colors = await response.json();
        displayPalette(colors);
    } catch (error) {
        console.error('Error generating palette:', error);
    }
}

async function generatePaletteFromHex(hex) {
    const rgb = hexToRgb(hex);
    generatePaletteFromRGBValues(rgb);
}

async function generatePaletteFromRGB(rgb) {
    const rgbValues = rgb.split(',').map(Number);
    generatePaletteFromRGBValues(rgbValues);
}

async function generatePaletteFromRGBValues(rgb) {
    try {
        const response = await fetch('http://127.0.0.1:5000/color_palette', {  // Change the URL if deployed on a remote server
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ color_value: `${rgb[0]},${rgb[1]},${rgb[2]}` })
        });
        const colors = await response.json();
        displayPalette(colors);
    } catch (error) {
        console.error('Error generating palette:', error);
    }
}

function hexToRgb(hex) {
    const bigint = parseInt(hex.slice(1), 16);
    return [(bigint >> 16) & 255, (bigint >> 8) & 255, bigint & 255];
}

function changeBackgroundColor(rgb) {
    document.body.style.backgroundColor = `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`;
}
