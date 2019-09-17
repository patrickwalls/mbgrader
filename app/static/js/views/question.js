var app = app || {};

app.QuestionView = Backbone.View.extend({

  tagName: 'tr',

  template: _.template($('#question').html()),

  initialize: function() {
    this.listenTo(this.model,'destroy remove',this.remove);
    this.listenTo(this.model,'sync',this.render);
  },

  render: function() {
    this.$el.html(this.template(this.model.attributes));
    return this;
  },

  events: {
    'click .delete_question': 'deleteQuestion',
    'click .create_batches': 'createBatches',
    'click .grade_batches': 'gradeBatches'
  },

  deleteQuestion: function() {
    this.model.destroy();
  },

  createBatches: function() {
    var url = 'assignments/' + this.model.get('assignment_id') + '/questions/' + this.model.get('id') + '/batches?create=true';
    app.AppRouter.navigate(url, {trigger: true});
  },

  gradeBatches: function() {
    var url = 'assignments/' + this.model.get('assignment_id') + '/questions/' + this.model.get('id') + '/batches?create=false';
    app.AppRouter.navigate(url, {trigger: true});
  }

});
