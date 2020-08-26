var app = app || {};

app.GradingView = Backbone.View.extend({

  el: '#grading',

  template: _.template($('#grade').html()),

  initialize: function() {
    this.listenTo(this.model,'sync',this.render);
  },

  render: function() {
    this.$el.html(this.template(this.model.attributes));
    if (this.model.get('datatype') == 'figure') {
      var lines = this.model.get('data');
      Plotly.newPlot('data', lines);
    };
    return this;
  },

  events: {
    'click #next-batch': 'nextBatch',
    'click #previous-batch': 'previousBatch',
    'click #submit-batch': 'submitBatch'
  },

  previousBatch: function() {
    var thisID = this.model.get('id');
    var thisIndex = app.AppBatches.findIndex((model) => model.get('id') == thisID);
    var prevIndex = (thisIndex - 1) % app.AppBatches.length;
    var prevID = app.AppBatches.at(prevIndex).get('id');
    var url = 'assignments/' + this.model.get('assignment_id') + '/questions/' + this.model.get('question_id') + '/batches/' + prevID;
    app.AppRouter.navigate(url, {trigger: true});
  },

  nextBatch: function() {
    var thisID = this.model.get('id');
    var thisIndex = app.AppBatches.findIndex((model) => model.get('id') == thisID);
    var nextIndex = (thisIndex + 1) % app.AppBatches.length;
    var nextID = app.AppBatches.at(nextIndex).get('id');
    var url = 'assignments/' + this.model.get('assignment_id') + '/questions/' + this.model.get('question_id') + '/batches/' + nextID;
    app.AppRouter.navigate(url, {trigger: true});
  },

  submitBatch: function() {
    var grade = this.$('#batch-grade').val();
    var comments = this.$('#batch-comments').val();
    this.model.save({'grade': grade, 'comments': comments},
    {
      success: function() {
      this.$('#batch-grade').val('');
      this.$('#batch-comments').val('');
    }
  });
}

});
