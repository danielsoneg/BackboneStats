var Stat = Backbone.Model.extend({
  // Our basic stat model. Required to hold data, not much else.
  initialize: function() {
    if(!this.get('params')){
      // Set defaults for new stats
      this.set('params',{who:'psng',what:'count',when:'week',fordate:'today'});
    }
  },
  url: function() {
    // Calculate our base url given model parameters
    return this.urlRoot + _.template("/<%=who %>/<%= what %>/<%=when %>/<%=fordate %>", this.get('params'));
  }
});

var StatCollection = Backbone.Collection.extend({
  // Our basic stat collection. For organization.
  model: Stat,
  url: 'Stats',
  initialize: function() {
    this.on("add", function(stat){
      // Set url, then update model.
      stat.urlRoot = this.url;
      stat.fetch();
    });
  }
});

var Stats = new StatCollection();

var StatView = Backbone.View.extend({
  // Our Stat View
  events: {
    "click .done" : "updateModel",
    "click .del" : "clear"
  },
  tagName: 'div',
  initialize: function() {
    this.model.bind('change:data', this.render,this);// Bind to data changes - stat has no data on init
    this.model.bind('destroy',this.remove,this);
    this.model.view = this;
  },
  render: function() {
    var data = this.model.get('data');
    var dataview = _.template(Templates.loading);
    var params = this.model.get('params');
    if (data !== undefined) {//Make sure we don't render an empty stat
      if (params.what == 'count') {
        dataview = _.template(Templates.counter);
      } else {
        if (data.length !== 0) { //Make sure we don't render empty chart
          dataview = _.template(Templates.chart);
        } else {
          dataview = _.template(Templates.empty);
        }
      }
    }
    dataview = dataview({data:data});
    var body = _.template(Templates.statTemplate);
    body = body({data:dataview,
          title:this.model.get('title'),
          edit:Templates.edit
          });
    this.$el.html(body);
    this.$el.attr('id','stat-' + this.model.cid).addClass('stat');
    if (params.what == 'top' && data.length !== 0) {//Render Chart
      this.$el.find('div.chart').attr('id','chart-' + this.model.cid);
      this.drawChart();
    }
    this.input = this.$('.edit');// Update edit form
    this.input.find('#who').val(params.who);
    this.input.find('#what').val(params.what);
    this.input.find('#when').val(params.when);
    this.input.find('#fordate').val(params.fordate);
    return this;
  },

  drawChart: function() {
    //Build bar chart using google API
    var data = this.model.get('data');
    var chartdata = [[this.model.get('params').who,'Miles']];
    if (this.model.get('params').who == 'rides') {
        _.each(data, function(d){ chartdata.push([d.psng.name + " & " + d.drvr.name, d.miles]); });
    } else {
        _.each(data,function(d){ chartdata.push([d.name,d.miles]);});
    }
    chartdata = google.visualization.arrayToDataTable(chartdata);
    var options = {
          title: this.model.get('title'),
          height: 80 + (data.length * 30)//Adjust size of chart.
        };
    var chart = new google.visualization.BarChart(document.getElementById("chart-" + this.model.cid));
    chart.draw(chartdata,options);
  },

  clear: function() {
    //Remove from StatCollection, clear model, and delete this view's element
    Stats.remove(this.model);
    this.model.clear({silent:true});
    this.remove();
  },
  updateModel: function() {
    // Read form, set model params, and trigger update.
    params = {};
    params.who = this.input.find('#who').val();
    params.what = this.input.find('#what').val();
    params.when = this.input.find('#when').val();
    params.fordate = this.input.find('#fordate').val();
    this.model.set('params',params);
    this.model.fetch();
  }
});

var StatPage = Backbone.View.extend({
  // Overall page container
  el: $('#container'),
  events: {
    "click #new" : "createStat",
    "click #refresh" : "updateStats",
  },
  
  initialize: function() {
    Stats.bind('add',this.addOne, this);
  },

  updateStats: function() {
    Stats.each(function(stat){stat.fetch();});
  },

  addOne: function(stat) {
    // Render a stat after it has been created
    var view = new StatView({model:stat});
    this.$('#main').append(view.render().el);
  },

  createStat: function() {
    Stats.create({title:"New Stat"});
  }
});

var App = new StatPage;
App.createStat();
