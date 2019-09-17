var app = app || {};

app.BatchView = Backbone.View.extend({

  tagName: 'tr',

  template: _.template($('#batch').html()),

  initialize: function() {
    this.listenTo(this.model,'remove',this.remove);
  },

  render: function() {
    this.$el.html(this.template(this.model.attributes));
    return this;
  },

  events: {
    'click .grade_batch': 'gradeBatch'
  },

  gradeBatch: function() {
    var url = 'assignments/' + this.model.get('assignment_id') + '/questions/' + this.model.get('question_id') + '/batches/' + this.model.get('id');
    app.AppRouter.navigate(url, {trigger: true});
  }

});
