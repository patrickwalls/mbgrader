var app = app || {};

$(function() {

  app.AppAssignments = new app.Assignments();
  app.AppAssignmentsView = new app.AssignmentsView({collection: app.AppAssignments});
  app.AppAssignments.fetch();

  app.AppQuestions = new app.Questions();
  app.AppQuestionsView = new app.QuestionsView({collection: app.AppQuestions});

  app.AppBatches = new app.Batches();
  app.AppBatchesView = new app.BatchesView({collection: app.AppBatches});

  app.AppBatch = new app.Batch();
  app.AppGradingView = new app.GradingView({model: app.AppBatch});

  app.AppRouter = new app.Router();

  Backbone.history.start();

});
