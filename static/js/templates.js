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
    <option class="psng" value="psng" <%=params.who == "psng" ? "selected" : "" %>>Passengers</option>\
    <option class="drvr" value="drvr" <%=params.who == "drvr" ? "selected" : "" %>>Drivers</option>\
    <option class="rides" value="rides" <%=params.who == "rides" ? "selected" : "" %>>Rides</option>\
  </select>\
  <select id="what">\
    <option value="count" <%=params.what == "count" ? "selected" : "" %>>Total</option>\
    <option value="top" <%=params.what == "top" ? "selected" : "" %>>Top</option>\
  </select>\
  <select id="when">\
    <option value="now" <%=params.when == "now" ? "selected" : "" %>>Today</option>\
    <option value="week" <%=params.when == "week" ? "selected" : "" %>>This Week</option>\
    <option value="month" <%=params.when == "month" ? "selected" : "" %>>This Month</option>\
    <option value="year" <%=params.when == "year" ? "selected" : "" %>>This Year</option>\
  </select>\
  <label class="fordate" for="for">For date (yyyy-mm-dd):</label><input type="text" id="fordate" name="fordate" value="<%=params.fordate %>"></input>\
  <input type="button" class="done" value="Update"></input>\
  <input type="button" class="del" value="Delete"></input>\
</form>'
};

window.Templates = Templates;