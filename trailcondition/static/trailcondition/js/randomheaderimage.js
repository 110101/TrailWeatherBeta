var headerimgarray = ['bg_fine_gravel.jpg','eric-muhr-@ericmuhr.jpg'];

function getRandomImage(imgArray) {
  var base_url = "url('/static/trailcondition/images/"; // default path here
  var num = Math.floor( Math.random() * imgArray.length );
  var img = imgArray[ num ];
  var img_url = base_url + img + "')";
  document.getElementById('backimage').style.backgroundImage = img_url;
}
