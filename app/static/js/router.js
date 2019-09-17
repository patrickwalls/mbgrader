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
    app.AppQuestionsView.$el.hide();
    app.AppBatchesView.$el.hide();
    app.AppGradingView.$el.hide();
    app.AppAssignmentsView.$el.show();
    this.makeNav(Backbone.history.getFragment());
  },

  questions: function(assignment_id) {
    app.AppQuestions.remove(app.AppQuestions.models);

    app.AppAssignmentsView.$el.hide();
    app.AppQuestionsView.$el.hide();
    app.AppBatchesView.$el.hide();
    app.AppGradingView.$el.hide();

    app.AppQuestions.url = 'assignments/' + assignment_id + '/questions';
    app.AppQuestions.fetch({
      reset: true,
      success: function() {
        app.AppQuestionsView.$el.show();
      }
    });
    this.makeNav(Backbone.history.getFragment());
  },

  batches: function(assignment_id,question_id,create) {
    app.AppBatches.remove(app.AppBatches.models);

    app.AppAssignmentsView.$el.hide();
    app.AppBatchesView.$el.hide();
    app.AppGradingView.$el.hide();

    if (create == 'true') {
      $('#creating-batches-modal-control').trigger('click');
    };
    app.AppBatches.url = 'assignments/' + assignment_id + '/questions/' + question_id + '/batches';
    app.AppBatches.fetch({
      data: {create: create},
      reset: true,
      success: function() {
        if (create == 'true') {
          $('#creating-batches-modal-control').trigger('click');
        };
        app.AppQuestionsView.$el.hide();
        app.AppBatchesView.$el.show();
      }
    });
    this.makeNav(Backbone.history.getFragment());
  },

  batchGrading: function(assignment_id,question_id,batch_id) {
    app.AppAssignmentsView.$el.hide();
    app.AppQuestionsView.$el.hide();
    app.AppBatchesView.$el.hide();

    app.AppBatch.url = 'assignments/' + assignment_id + '/questions/' + question_id + '/batches/' + batch_id;
    app.AppBatch.fetch({
      success: function() {
        app.AppGradingView.render();
        app.AppGradingView.$el.show();
      }
    });
    this.makeNav(Backbone.history.getFragment());
  },

  makeNav: function(url) {
    var url_frags = url.split('/');
    $('#nav-assignment').hide();
    $('#nav-question').hide();

    if (url_frags.length >= 3) {
      $('#nav-assignment').html(app.AppAssignments.get(parseInt(url_frags[1])).get('name'));
      $('#nav-assignment').attr('href','#' + url_frags.slice(0,3).join('/'));
      $('#nav-assignment').show();
    }

    if (url_frags.length >= 5) {
      $('#nav-question').html(app.AppQuestions.get(parseInt(url_frags[3])).get('name'));
      $('#nav-question').attr('href', '#' + url_frags.slice(0,4).join('/') + '/batches?create=false');
      $('#nav-question').show();
    }
  }

});
