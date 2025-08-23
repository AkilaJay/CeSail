// Function to create and position the canvas overlay
function createCanvasOverlay() {
    const canvas = document.createElement('canvas');
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.pointerEvents = 'none'; // Allow clicking through the canvas
    canvas.style.zIndex = '9999';
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    document.body.appendChild(canvas);
    return canvas;
}

// Function to generate random color
function getRandomColor() {
    const hue = Math.floor(Math.random() * 360); // Random hue
    return `hsla(${hue}, 70%, 50%, 0.8)`; // HSL with alpha for stroke
}

// Function to get lighter version of a color for fill
function getLighterColor(color) {
    return color.replace('0.8', '0.1'); // Replace alpha for fill
}

// Function to draw bounding boxes
export function drawBoundingBoxes(elements) {
    // Create or get canvas
    let canvas = document.querySelector('#bounding-boxes-canvas');
    if (!canvas) {
        canvas = createCanvasOverlay();
        canvas.id = 'bounding-boxes-canvas';
    }

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Track used label positions to prevent overlap
    const usedLabelPositions = new Set();
    
    // Helper function to check if a position is available
    const isPositionAvailable = (x, y, width, height) => {
        const key = `${Math.floor(x)},${Math.floor(y)},${Math.floor(width)},${Math.floor(height)}`;
        return !usedLabelPositions.has(key);
    };
    
    // Helper function to mark position as used
    const markPositionUsed = (x, y, width, height) => {
        const key = `${Math.floor(x)},${Math.floor(y)},${Math.floor(width)},${Math.floor(height)}`;
        usedLabelPositions.add(key);
    };
    
    // Helper function to find available position for label
    const findAvailablePosition = (elementX, elementY, elementWidth, elementHeight, labelWidth, labelHeight) => {
        const positions = [
            // Above the element
            { x: elementX, y: elementY - labelHeight - 5 },
            // Below the element
            { x: elementX, y: elementY + elementHeight + 5 },
            // Left of the element
            { x: elementX - labelWidth - 5, y: elementY },
            // Right of the element
            { x: elementX + elementWidth + 5, y: elementY },
            // Top-left corner
            { x: elementX - labelWidth - 5, y: elementY - labelHeight - 5 },
            // Top-right corner
            { x: elementX + elementWidth + 5, y: elementY - labelHeight - 5 },
            // Bottom-left corner
            { x: elementX - labelWidth - 5, y: elementY + elementHeight + 5 },
            // Bottom-right corner
            { x: elementX + elementWidth + 5, y: elementY + elementHeight + 5 }
        ];
        
        for (const pos of positions) {
            if (isPositionAvailable(pos.x, pos.y, labelWidth, labelHeight)) {
                return pos;
            }
        }
        
        // If no position is available, return a position with offset
        return { x: elementX + Math.random() * 50, y: elementY + Math.random() * 50 };
    };

    // Draw each bounding box
    elements.forEach(element => {
        try {
            // Check if element has the expected structure
            if (!element || !element.bbox || typeof element.bbox.x === 'undefined') {
                console.warn('Element missing bbox property:', element);
                return; // Skip this element
            }

            const strokeColor = getRandomColor();
            const fillColor = getLighterColor(strokeColor);
            
            // Convert normalized bbox coordinates to pixel coordinates
            const x = element.bbox.x * canvas.width;
            const y = element.bbox.y * canvas.height;
            const width = element.bbox.w * canvas.width;
            const height = element.bbox.h * canvas.height;
            
            ctx.strokeStyle = strokeColor;
            ctx.lineWidth = 2;
            ctx.strokeRect(x, y, width, height);

            // Add a semi-transparent fill
            ctx.fillStyle = fillColor;
            ctx.fillRect(x, y, width, height);
            
            // Create label text
            const selector = element.selector || 'N/A';
            const label = `${selector}`;
            
            // Set font and measure text
            ctx.font = 'bold 18px Arial';
            ctx.textBaseline = 'middle';
            ctx.textAlign = 'center';
            const labelMetrics = ctx.measureText(label);
            const labelWidth = labelMetrics.width;
            const labelHeight = 20; // Approximate height for 18px font
            
            // Calculate center position of the element
            const centerX = x + width / 2;
            const centerY = y + height / 2;
            
            // Draw label background for better readability
            // ctx.fillStyle = 'rgba(255, 255, 255, 1.0)';
            // ctx.fillRect(centerX - labelWidth/2 - 4, centerY - labelHeight/2 - 2, labelWidth + 8, labelHeight + 4);
            
            // Draw text shadow/halo effect for better readability
            ctx.fillStyle = 'rgba(0, 0, 0, 0.8)'; // Black shadow
            ctx.fillText(label, centerX - 1, centerY - 1);
            ctx.fillText(label, centerX + 1, centerY - 1);
            ctx.fillText(label, centerX - 1, centerY + 1);
            ctx.fillText(label, centerX + 1, centerY + 1);
            
            // Draw main label text
            ctx.fillStyle = strokeColor;
            ctx.fillText(label, centerX, centerY);
            
            // Print selector to console
            console.log(`Element ${selector}`);
            
        } catch (error) {
            console.error('Error drawing bounding box for element:', element, error);
        }
    });
}

// Function to handle window resize
function handleResize() {
    const canvas = document.querySelector('#bounding-boxes-canvas');
    if (canvas) {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        // Redraw boxes after resize
        try {
            const elements = window.getTopLevelElements ? window.getTopLevelElements() : [];
            if (elements && elements.length > 0) {
                drawBoundingBoxes(elements);
            }
        } catch (error) {
            console.error('Error redrawing bounding boxes after resize:', error);
        }
    }
}

// Function to toggle visualization
export function toggleVisualization() {
    const canvas = document.querySelector('#bounding-boxes-canvas');
    if (canvas) {
        canvas.remove();
    } else {
        try {
            const elements = window.getTopLevelElements ? window.getTopLevelElements() : [];
            if (elements && elements.length > 0) {
                drawBoundingBoxes(elements);
            } else {
                console.warn('No elements found to visualize');
            }
        } catch (error) {
            console.error('Error toggling visualization:', error);
        }
    }
}

// Function to clear the canvas
export function clearCanvas() {
    const canvas = document.querySelector('#bounding-boxes-canvas');
    if (canvas) {
        canvas.remove();
        console.log('Canvas cleared');
    } else {
        console.log('No canvas found to clear');
    }
}

// Function to draw a dot at given coordinates
export function drawDot(x, y, color = 'red', size = 15) {
    // Create or get canvas
    let canvas = document.querySelector('#bounding-boxes-canvas');
    if (!canvas) {
        canvas = createCanvasOverlay();
        canvas.id = 'bounding-boxes-canvas';
    }

    const ctx = canvas.getContext('2d');
    
    // Save the current context state
    ctx.save();
    
    // Set the dot properties
    ctx.fillStyle = color;
    ctx.strokeStyle = 'black';
    ctx.lineWidth = 2;
    
    // Draw the dot (circle)
    ctx.beginPath();
    ctx.arc(x, y, size, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();
    
    // Add a white center for better visibility
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(x, y, size * 0.6, 0, 2 * Math.PI);
    ctx.fill();
    
    // Restore the context state
    ctx.restore();
    
    console.log(`Drew ${color} dot at (${x}, ${y}) with size ${size}`);
}

// Function to draw a ruler with labels every 50px
export function drawRuler() {
    // Create or get canvas
    let canvas = document.querySelector('#bounding-boxes-canvas');
    if (!canvas) {
        canvas = createCanvasOverlay();
        canvas.id = 'bounding-boxes-canvas';
    }

    const ctx = canvas.getContext('2d');
    
    // Save the current context state
    ctx.save();
    
    const width = canvas.width;
    const height = canvas.height;
    
    // Set ruler properties (more transparent)
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.4)';
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.lineWidth = 1;
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    // Draw horizontal ruler (top)
    ctx.beginPath();
    ctx.moveTo(0, 20);
    ctx.lineTo(width, 20);
    ctx.stroke();
    
    // Draw vertical ruler (left)
    ctx.beginPath();
    ctx.moveTo(20, 0);
    ctx.lineTo(20, height);
    ctx.stroke();
    
    // Draw horizontal tick marks and labels (every 50px)
    for (let x = 0; x <= width; x += 50) {
        // Draw tick mark
        ctx.beginPath();
        ctx.moveTo(x, 15);
        ctx.lineTo(x, 25);
        ctx.stroke();
        
        // Draw label
        ctx.fillText(x.toString(), x, 8);
    }
    
    // Draw vertical tick marks and labels (every 50px)
    for (let y = 0; y <= height; y += 50) {
        // Draw tick mark
        ctx.beginPath();
        ctx.moveTo(15, y);
        ctx.lineTo(25, y);
        ctx.stroke();
        
        // Draw label (rotated for vertical ruler)
        ctx.save();
        ctx.translate(8, y);
        ctx.rotate(-Math.PI / 2);
        ctx.fillText(y.toString(), 0, 0);
        ctx.restore();
    }
    
    // Draw corner label (more transparent)
    ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
    ctx.fillRect(0, 0, 30, 30);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.font = 'bold 10px Arial';
    ctx.fillText('0,0', 15, 15);
    
    // Restore the context state
    ctx.restore();
    
    console.log(`Drew ruler for ${width}x${height} viewport`);
}

// Add event listeners
window.addEventListener('resize', handleResize);

// Export functions to global scope for compatibility
window.drawBoundingBoxes = drawBoundingBoxes;
window.toggleVisualization = toggleVisualization;
window.clearCanvas = clearCanvas;
window.drawDot = drawDot;
window.drawRuler = drawRuler;
