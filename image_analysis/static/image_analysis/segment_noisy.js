function generateColorShifts() {
    var canvas = document.getElementById("mainCanvas"); 
    var context = canvas.getContext("2d");
    
    window.redNoise = new Array();    
    window.greenNoise = new Array(); 
    window.blueNoise = new Array(); 

    var imgData = context.getImageData(0,0,canvas.width,canvas.height);
    var data = imgData.data;

    for (i = 0; i < data.length; i += 4) 
    {                     
      window.redNoise[i] = Math.floor( (Math.random()-0.5) * 100 );
      window.greenNoise[i] = Math.floor( (Math.random()-0.5) * 100 );
      window.blueNoise[i] = Math.floor( (Math.random()-0.5) * 100 );
    } 
}

function applySegmentColorMask(){
    var canvas = document.getElementById("mainCanvas"); 
    var context = canvas.getContext("2d");
    var media = document.getElementById("img");
  
    context.drawImage( media, 0, 0, media.width, media.height, 0, 0, canvas.width, canvas.height);
  
    var imgData = context.getImageData(0,0,canvas.width,canvas.height);
    var data = imgData.data;
  
    var red = new Array();    
    var green = new Array(); 
    var blue = new Array(); 
    var alpha = new Array();    
  
    var redShift;
    var greenShift;
  
    for (i = 0; i < data.length; i += 4) 
    {                     
      if (window.segmentLabeled[i/4] == 0) {
          redShift = 80;
          greenShift = 0;
      } else {
          redShift = 0;
          greenShift = 80;
      }
      red[i] = Math.min(imgData.data[i] + redShift, 255);
      green[i] = Math.min(imgData.data[i+1] + greenShift, 255);
      blue[i] = imgData.data[i+2];
      alpha[i] = imgData.data[i+3];
    } 
  
    for (i = 0; i < data.length; i += 4)  
    {
      imgData.data[i] = red[i] + window.redNoise[i];
      imgData.data[i+1] = green[i] + window.greenNoise[i];
      imgData.data[i+2] = blue[i] + window.blueNoise[i]; 
      imgData.data[i+3] = alpha[i];   
    } 
  
    context.putImageData(imgData, 0, 0);
  } 
  
  function applyBrush(canvas, event) {
      const rect = canvas.getBoundingClientRect();
      const x = Math.floor(event.offsetX * (canvas.width / rect.width));
      const y = Math.floor(event.offsetY * (canvas.height / rect.height));
  
  
      if(event.buttons == 1){
          var slider = document.getElementById("brushSizeSlider");
          var radius = slider.value;
          var media = document.getElementById("img");
          
          for (let dx = -radius; dx <= radius; dx++) {
              for (let dy = -radius; dy <= radius; dy++) {
                  if (Math.pow(dx, 2) + Math.pow(dy, 2) < Math.pow(radius, 2)) {
                      window.segmentLabeled[((y+dy) * media.width) + x + dx] = (1 ? window.brushIsGreen == true : 0);
                  }
              }
          }        
  
          applySegmentColorMask();
      }
  }
  
  
  window.onload = function() {
      var canvas = document.getElementById("mainCanvas");
      var context = canvas.getContext("2d");
      var media = document.getElementById("img");
  
      canvas.width = media.width;
      canvas.height = media.height;
  
      context.drawImage( media, 0, 0, media.width, media.height, 0, 0, canvas.width, canvas.height);
  
      window.segmentLabeled = Array(canvas.width*canvas.height).fill(0);
      generateColorShifts();
      window.brushIsGreen = true;
  
      canvas.addEventListener('mousemove', function(e) {
          applyBrush(canvas, e)
      })
  
      canvas.addEventListener('mousedown', function(e) {
          applyBrush(canvas, e)
      })
  
      var redButton = document.getElementById("redBrushButton");
      var greenButton = document.getElementById("greenBrushButton");
  
      redButton.onclick = function () {window.brushIsGreen = false;};
      greenButton.onclick = function () {window.brushIsGreen = true;};
  
      var nextButton = document.getElementById("nextButton");
  
      nextButton.onclick = function () {
          var toUpload = new File([JSON.stringify(window.segmentLabeled)], "seg_data.json", {type: "text/json"});
  
          const dataTransfer = new DataTransfer();
          dataTransfer.items.add(toUpload);
      
          document.getElementById("id_data").files = dataTransfer.files;
          document.getElementById("id_noisy").checked = true;
  
          document.getElementById("form").submit();
      }
  
      applySegmentColorMask();
  };
  