var app = app || {};

app.AppNavigationView = new app.NavigationView();
app.AppAssignmentsView = new app.AssignmentsView({collection: new app.Assignments()});
app.AppQuestionsView = new app.QuestionsView({collection: new app.Questions()});
app.AppBatchesView = new app.BatchesView({collection: new app.Batches()});
app.AppGradingView = new app.GradingView({model: new app.Batch()});
app.AppRouter = new app.Router();
app.clear = function () {
    app.AppAssignmentsView.collection.remove(app.AppAssignmentsView.collection.models);
    app.AppQuestionsView.collection.remove(app.AppQuestionsView.collection.models);
    app.AppBatchesView.collection.remove(app.AppBatchesView.collection.models);
    app.AppGradingView.model.clear();
    app.AppNavigationView.$el.html('');
    app.AppAssignmentsView.$el.hide();
    app.AppQuestionsView.$el.hide();
    app.AppBatchesView.$el.hide();
    app.AppGradingView.$el.hide();
};

Backbone.history.start();