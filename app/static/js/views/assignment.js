var app = app || {};

app.AssignmentView = Backbone.View.extend({

  tagName: 'tr',

  template: _.template($('#assignment').html()),

  initialize: function() {
    this.listenTo(this.model,'destroy remove',this.remove);
    this.listenTo(this.model,'sync',this.render);
  },

  render: function() {
    this.$el.html(this.template(this.model.attributes));
    return this;
  },

  events: {
    'click .grade': 'gradeAssignment',
    'click .delete': 'deleteAssignment'
  },

  gradeAssignment: function () {
    var url = 'assignments/' + this.model.get('id') + '/questions';
    app.AppRouter.navigate(url, {trigger: true});
  },

  deleteAssignment: function() {
    this.model.destroy();
  }

});
