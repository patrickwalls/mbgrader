var app = app || {};

app.Assignments = Backbone.Collection.extend({ model : app.Assignment , url: '/assignments' });

app.Questions = Backbone.Collection.extend({
    
    model : app.Question,
    
    makeURL : function(assignment_id) {
      this.url = '/assignments/' + assignment_id + '/questions';
      return this;
    }

});

app.Batches = Backbone.Collection.extend({
    
    model: app.Batch,

    makeURL: function(assignment_id,question_id) {
      this.url = '/assignments/' + assignment_id + '/questions/' + question_id + '/batches';
      return this;
    },
    
    comparator: function(batch) {
      return -batch.get('total_batch_responses');
    }

  });