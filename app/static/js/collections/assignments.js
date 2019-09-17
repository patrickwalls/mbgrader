var app = app || {};

app.Assignments = Backbone.Collection.extend({
    model: app.Assignment,
    url: '/assignments'
  });
