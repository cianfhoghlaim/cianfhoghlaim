function safeString(text) {
    if (!text) return '';
    try {
        return String(text);
    } catch (e) {
        return 'Error displaying text';
    }
}

function escapeHtml(text) {
    if (!text) return '';
    try {
        var str = safeString(text);
        var map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return str.replace(/[&<>"']/g, function(m) { return map[m] || m; });
    } catch (e) {
        return 'Error displaying text';
    }
}

function formatTextSafely(text, maxLength) {
    if (!text) return '<em>Not available</em>';

    try {
        var safeText = escapeHtml(safeString(text));
        if (!safeText || safeText.trim() === '') return '<em>Not available</em>';

        safeText = safeText.replace(/\\n/g, '<br>').replace(/\\r/g, '<br>');

        var rtlPattern = /[\u0590-\u05FF\u0600-\u06FF\u0750-\u077F]/;
        var isRTL = rtlPattern.test(safeText);
        var dirAttr = isRTL ? ' dir="rtl"' : '';

        if (safeText.length > maxLength) {
            var shortText = safeText.substring(0, maxLength);
            return '<div class="text-content"' + dirAttr + '>' +
                   '<span class="short-text">' + shortText + '...</span>' +
                   '<span class="full-text" style="display: none;">' + safeText + '</span>' +
                   '<br><a href="#" onclick="toggleText(this); return false;" class="toggle-link">Show more</a>' +
                   '</div>';
        }

        return '<div' + dirAttr + '>' + safeText + '</div>';
    } catch (e) {
        console.error('Error formatting text:', e);
        return '<em>Error displaying content</em>';
    }
}

function toggleText(link) {
    try {
        var container = link.parentElement;
        var shortText = container.querySelector('.short-text');
        var fullText = container.querySelector('.full-text');

        if (fullText && shortText) {
            if (fullText.style.display === 'none') {
                shortText.style.display = 'none';
                fullText.style.display = 'inline';
                link.textContent = 'Show less';
            } else {
                shortText.style.display = 'inline';
                fullText.style.display = 'none';
                link.textContent = 'Show more';
            }
        }
    } catch (e) {
        console.error('Error toggling text:', e);
    }
}

function closePopup() {
    try {
        var popup = document.getElementById('enhanced-popup');
        var overlay = document.getElementById('popup-overlay');
        if (popup) popup.style.display = 'none';
        if (overlay) overlay.style.display = 'none';
    } catch (e) {
        console.error('Error closing popup:', e);
    }
}

function safeGetCustomData(point, index, fallback) {
    try {
        if (point && point.customdata && point.customdata[index] !== undefined) {
            return point.customdata[index];
        }
        return fallback || '';
    } catch (e) {
        console.error('Error getting custom data at index', index, ':', e);
        return fallback || '';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    try {
        var plotDiv = document.querySelector('.plotly-graph-div');
        if (!plotDiv) {
            console.warn('Plotly graph div not found');
            return;
        }

        plotDiv.on('plotly_click', function(data){
            try {
                if (!data || !data.points || !data.points[0]) {
                    console.warn('No point data available');
                    return;
                }

                var point = data.points[0];
                var docId = safeGetCustomData(point, 0, 'Unknown Document');
                var language = safeGetCustomData(point, 1, 'Unknown');
                var hasImage = safeGetCustomData(point, 2, false);
                var hasTranscription = safeGetCustomData(point, 3, false);
                var imageData = safeGetCustomData(point, 6, '');
                var fullDescription = safeGetCustomData(point, 7, '');
                var fullTranscription = safeGetCustomData(point, 8, '');
                var originalImageUrl = safeGetCustomData(point, 9, ''); // Get original image URL

                var popup = document.getElementById('enhanced-popup');
                if (!popup) {
                    popup = document.createElement('div');
                    popup.id = 'enhanced-popup';
                    popup.style.position = 'fixed';
                    popup.style.top = '50%';
                    popup.style.left = '50%';
                    popup.style.transform = 'translate(-50%, -50%)';
                    popup.style.background = 'white';
                    popup.style.border = '2px solid #333';
                    popup.style.borderRadius = '12px';
                    popup.style.padding = '0';
                    popup.style.zIndex = '9999';
                    popup.style.boxShadow = '0 8px 32px rgba(0,0,0,0.3)';
                    popup.style.maxWidth = '90vw';
                    popup.style.maxHeight = '90vh';
                    popup.style.overflow = 'hidden';
                    popup.style.display = 'flex';
                    popup.style.flexDirection = 'column';
                    document.body.appendChild(popup);

                    var overlay = document.createElement('div');
                    overlay.id = 'popup-overlay';
                    overlay.style.position = 'fixed';
                    overlay.style.top = '0';
                    overlay.style.left = '0';
                    overlay.style.width = '100%';
                    overlay.style.height = '100%';
                    overlay.style.background = 'rgba(0,0,0,0.6)';
                    overlay.style.zIndex = '9998';
                    overlay.onclick = closePopup;
                    document.body.appendChild(overlay);
                }

                var imageSection = '';
                if (imageData && imageData !== "No image available" && imageData.indexOf && imageData.indexOf('data:image') === 0) {
                    if (originalImageUrl && originalImageUrl.trim() !== '') {
                        imageSection = '<div style="text-align: center; padding: 0; background: #f8f9fa;"><a href="' + originalImageUrl + '" target="_blank"><img src="' + imageData + '" style="max-width: 100%; max-height: 40vh; object-fit: contain; display: block;" alt="Document image"></a></div>';
                    } else {
                        imageSection = '<div style="text-align: center; padding: 0; background: #f8f9fa;"><img src="' + imageData + '" style="max-width: 100%; max-height: 40vh; object-fit: contain; display: block;" alt="Document image"></div>';
                    }
                } else {
                    imageSection = '<div style="text-align: center; padding: 20px; background: #f8f9fa; color: #666;"><em>No image available</em></div>';
                }

                var imageIcon = hasImage ? 'Yes' : 'No';
                var transcriptionIcon = hasTranscription ? 'Yes' : 'No';

                popup.innerHTML =
                    '<div style="background: #2c3e50; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center;">' +
                        '<div style="flex: 1; min-width: 0;">' +
                            '<h2 style="margin: 0; font-size: 1.2em; word-break: break-word;">' + escapeHtml(docId) + '</h2>' +
                            '<p style="margin: 5px 0 0 0; opacity: 0.8; font-size: 0.9em;">' +
                                'Language: ' + escapeHtml(language) + ' | ' +
                                'Image: ' + imageIcon + ' | ' +
                                'Transcription: ' + transcriptionIcon +
                            '</p>' +
                        '</div>' +
                        '<button onclick="closePopup();" style="border: none; background: #e74c3c; color: white; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 16px; margin-left: 15px;">Close</button>' +
                    '</div>' +
                    imageSection +
                    '<div style="flex: 1; overflow-y: auto; padding: 20px;">' +
                        '<div style="margin-bottom: 25px;">' +
                            '<h3 style="margin: 0 0 10px 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">Description</h3>' +
                            '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #3498db; line-height: 1.6; word-wrap: break-word;">' +
                                formatTextSafely(fullDescription, 800) +
                            '</div>' +
                        '</div>' +
                        '<div>' +
                            '<h3 style="margin: 0 0 10px 0; color: #2c3e50; border-bottom: 2px solid #27ae60; padding-bottom: 5px;">Transcription</h3>' +
                            '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #27ae60; line-height: 1.8; font-family: Arial, sans-serif; font-size: 1.1em; word-wrap: break-word; white-space: pre-wrap;">' +
                                formatTextSafely(fullTranscription, 1000) +
                            '</div>' +
                        '</div>' +
                    '</div>';

                if (!document.querySelector('#popup-styles')) {
                    var style = document.createElement('style');
                    style.id = 'popup-styles';
                    style.textContent = '.toggle-link { color: #3498db; text-decoration: none; font-weight: bold; font-size: 0.9em; } .toggle-link:hover { color: #2980b9; text-decoration: underline; } [dir="rtl"] { text-align: right; }';
                    document.head.appendChild(style);
                }

                popup.style.display = 'flex';
                document.getElementById('popup-overlay').style.display = 'block';

            } catch (e) {
                console.error('Error handling click event:', e);
                alert('Error displaying document details');
            }
        });
    } catch (e) {
        console.error('Error setting up click handler:', e);
    }
});