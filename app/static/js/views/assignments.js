var app = app || {};

app.AssignmentsView = Backbone.View.extend({

  el: '#assignments',

  initialize: function() {
    this.listenTo(this.collection,'sync',this.render)
  },

  render: function() {
    this.$('tbody').empty();
    this.collection.each(function(assignment) {
      var assignmentView = new app.AssignmentView({model: assignment});
      this.$('tbody').append(assignmentView.render().el);
    }, this);
  },

  events: {
    'click #create_assignment': 'createAssignment'
  },

  createAssignment: function() {
    this.$('#assignment-modal-close').trigger('click');
    this.$('#loading-submissions-modal-control').trigger('click');
    var name = this.$('#new_assignment_name').val();
    this.$('#new_assignment_name').val('');
    var assignment = this.collection.create({'name': name},{
      success: function() {
        this.$('#loading-submissions-modal-control').trigger('click');
      }
    });
  }

});
