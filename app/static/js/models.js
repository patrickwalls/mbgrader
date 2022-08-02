var app = app || {};

app.Assignment = Backbone.Model.extend({});

app.Question = Backbone.Model.extend({});

app.Batch = Backbone.Model.extend({

    makeURL: function(assignment_id,question_id,batch_id) {
      this.url = '/assignments/' + assignment_id + '/questions/' + question_id + '/batches/' + batch_id;
      return this;
    }

});