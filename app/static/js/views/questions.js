var app = app || {};

app.QuestionsView = Backbone.View.extend({
  el: '#questions',

  initialize: function() {
    this.listenTo(this.collection,'reset',this.render);
  },

  render: function() {
    this.collection.each(this.renderQuestion,this);
  },

  renderQuestion: function(question) {
    var questionView = new app.QuestionView({model: question});
    this.$('table').append(questionView.render().el);
  },

  events: {
    'click #create_question': 'createQuestion',
    'click #save_grades': 'saveGrades',
    'click #get_vars': 'getVars',
    'click #create_response': 'createResponse'
  },

  createQuestion: function() {
    var name = this.$('#new_question_name').val();
    var var_name = this.$('#new_var_name').val();
    var alt_var_name = this.$('#new_alt_var_name').val();
    var max_grade = this.$('#new_max_grade').val();
    var tolerance = this.$('#new_tolerance').val();
    var preprocessing = this.$('#new_preprocessing').val();

    var question = this.collection.create({
      'name': name,
      'var_name': var_name,
      'alt_var_name': alt_var_name,
      'max_grade': max_grade,
      'tolerance': tolerance,
      'preprocessing': preprocessing,
      'total_batches': 0
    });

    this.renderQuestion(question);

    this.$('#new_question_name').val('');
    this.$('#new_var_name').val('');
    this.$('#new_alt_var_name').val('');
    this.$('#new_max_grade').val('');
    this.$('#new_tolerance').val('');
    this.$('#new_preprocessing').val('');

    this.$('#question-modal-close').trigger('click');
  },

  saveGrades: function() {
    var url = 'assignments/' + this.collection.assignment_id + '/grades';
    $.get(url, function() {
        $('#grades-modal-control').trigger('click');
      });
  },

  getVars: function() {
    var url = 'assignments/' + this.collection.assignment_id + '/vars';
    $.get(url, function(data) {
      $('#vars').html(data.vars.join('<br>'));
    });
  },

  createResponse: function() {
    var name = this.$('#new_response_name').val();
    var vars = this.$('#new_response_vars').val();
    var expression = this.$('#new_response_expression').val();
    var extension = this.$('#new_response_extension').val();
    var data = {'name': name, 'vars': vars, 'expression': expression, 'extension': extension};
    var url = 'assignments/' + this.collection.assignment_id + '/response';
    $('#response-modal-close').trigger('click');
    $('#creating-responses-modal-control').trigger('click');
    $.post(url,data, function() {
        $('#creating-responses-modal-control').trigger('click');
      });

    this.$('#new_response_name').val('');
    this.$('#new_response_vars').val('');
    this.$('#new_response_expression').val('');
    this.$('#new_response_exstension').val('');
  }

});
