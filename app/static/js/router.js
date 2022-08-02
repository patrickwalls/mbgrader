var app = app || {};

app.Router = Backbone.Router.extend({

  routes: {
    '': 'assignments',
    'assignments': 'assignments',
    'assignments/:assignment_id/questions': 'questions',
    'assignments/:assignment_id/questions/:question_id/batches?create=:create': 'batches',
    'assignments/:assignment_id/questions/:question_id/batches/:batch_id': 'batchGrading'
  },

  assignments: function() {
    app.clear();
    app.AppAssignmentsView.collection.fetch({
      success: function() {
        app.AppAssignmentsView.$el.show();
      }
    });
  },

  questions: function(assignment_id) {
    app.clear();
    app.AppQuestionsView.collection.assignment_id = assignment_id;
    app.AppQuestionsView.collection.makeURL(assignment_id);
    app.AppQuestionsView.collection.fetch({
      reset: true,
      success: function() {
        app.AppNavigationView.render(assignment_id,null);
        app.AppQuestionsView.$el.show();
      }
    });
  },

  batches: function(assignment_id,question_id,create) {
    app.clear();
    if (create == 'true') {
      $('#creating-batches-modal-control').trigger('click');
    };
    app.AppBatchesView.collection.makeURL(assignment_id,question_id);
    app.AppBatchesView.collection.fetch({
      data: {create: create},
      reset: true,
      success: function() {
        if (create == 'true') {
          $('#creating-batches-modal-control').trigger('click');
        };
        app.AppNavigationView.render(assignment_id,question_id);
        app.AppBatchesView.$el.show();
      }
    });
  },

  batchGrading: function(assignment_id,question_id,batch_id) {
    app.clear();
    app.AppGradingView.model.makeURL(assignment_id,question_id,batch_id);
    app.AppGradingView.model.fetch({
      success: function() {
        app.AppNavigationView.render(assignment_id,question_id);
        app.AppGradingView.$el.show();
      }
    });
  }

});