var app = app || {};

app.BatchesView = Backbone.View.extend({

  el: '#batches',

  initialize: function() {
    this.listenTo(this.collection,'reset',this.render);
  },

  render: function() {
    this.collection.sort();
    this.collection.each(this.renderBatch,this);
  },

  renderBatch: function(batch) {
    var batchView = new app.BatchView({model: batch});
    this.$('tbody').append(batchView.render().el);
  }

});
