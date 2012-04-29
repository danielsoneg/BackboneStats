/*jshint multistr:true laxcomma:true */

Templates = {
  empty : '<div class="empty">No data available for this date range</div>'
  , loading : '<div class="loading"/>'
  
  , chart : '<div class="chart"></div>'
  , counter: '<div class="counter"><%=data %><div>'

  , statTemplate : '<div class="large">\
  <h1 class="title"><%=title %></h1>\
    <%=edit %>\
  <div class="data">\
    <%=data %>\
  </div>\
</div>'

  , edit : '<form class="edit">\
  <select id="who">\
    <option class="psng" value="psng">Passengers</option>\
    <option class="drvr" value="drvr">Drivers</option>\
    <option class="rides" value="rides">Rides</option>\
  </select>\
  <select id="what">\
    <option value="count">Total</option>\
    <option value="top">Top</option>\
  </select>\
  <select id="when">\
    <option value="now">Today</option>\
    <option value="week">This Week</option>\
    <option value="month">This Month</option>\
    <option value="year">This Year</option>\
  </select>\
  <label class="fordate" for="for">For date (yyyy-mm-dd):</label><input type="text" id="fordate" name="fordate"></input>\
  <input type="button" class="done" value="Update"></input>\
  <input type="button" class="del" value="Delete"></input>\
</form>'
};

window.Templates = Templates;