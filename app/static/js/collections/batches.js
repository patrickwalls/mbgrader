var app = app || {};

app.Batches = Backbone.Collection.extend({
    model: app.Batch,

    comparator: function(batch) {
      return -batch.get('total_batch_responses');
    }

  });
