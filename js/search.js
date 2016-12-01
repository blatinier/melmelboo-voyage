$(function(){
  function search() {
      var txt = $('input#search').val()
      var url = "//" + window.location.host + "/search/?q=" + txt;
      window.location.replace(url)
  }
  $('input#search').on('keydown', function(e) {
      if (e.which == 13) {
          e.preventDefault();
          search();
      }
  });
  $('input#submit-search').on('click', function(e) {
      e.preventDefault();
      search();
  });
});
