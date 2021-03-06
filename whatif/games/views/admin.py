from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from whatif.games.documents import Game, Token, Question, TokenModifier

# encapsulated template referrence
def _template(name):
    return 'admin/%s.html' % name

# util method for easy http responses
def _respond(template, context, request):
    return render_to_response(_template(template), 
                _with_game_form(context), 
                context_instance=RequestContext(request))
    
# util to add the 'New Game' form to the context which exists on all admin pages
def _with_game_form(context):
    context['game_form'] = Game.GameForm()
    return context

# util method for retrieving a game and raising a 404 if its not found
def _get_game_or_404(game_id):
    try:
        return Game.objects.with_id(game_id)
    except:
        raise Http404
    
# util method for retrieving a token and raising a 404 if its not found
def _get_token_or_404(token_id):
    try:
        return Token.objects.with_id(token_id)
    except:
        raise Http404
    
# util method for retrieving a question and raising a 404 if its not found
def _get_question_or_404(question_id):
    try:
        return Question.objects.with_id(question_id)
    except:
        raise Http404

# Admin index page.
@login_required
def admin_index(request):
    return _respond('index', { "games": Game.objects, }, request)

# POST endpoint for adding a new game. We only need the title to get started
@login_required
def new_game(request):
    if request.method == 'POST':
        form = Game.GameForm(request.POST)
        if form.is_valid():
            game = Game(**form.cleaned_data)
            game.save()
            return HttpResponseRedirect('/admin/%s/edit/' % game.id)
    else:
        return HttpResponseRedirect('/admin/')

# Edit game page
@login_required
def edit_game(request, game_id):
    game = _get_game_or_404(game_id)
    context = {
        "game": game,
        "token_form": Token.TokenForm()
    }
    return _respond('edit-game', context, request)

# POST endpoint for adding a token to a game
@login_required
def add_token(request, game_id):
    game = _get_game_or_404(game_id)
    token = Token(text=request.POST.get('token_text'))
    token.save()
    game.tokens.append(token)
    
    for question in game.questions:
        question.token_modifiers.append(TokenModifier(token=token, yes_modifier=0, no_modifier=0))
        question.save()
        
    game.save()
    return HttpResponseRedirect('/admin/%s/edit/' % str(game.id))

# Endpoint for removing a token form a game
@login_required
def remove_token(request, game_id, token_id):
    game = _get_game_or_404(game_id)
    token = _get_token_or_404(token_id)
    game.tokens.remove(token)
    
    for question in game.questions:
        for modifier in question.token_modifiers:
            if modifier.token.id == token.id:
                question.token_modifiers.remove(modifier)
        question.save()
        
    game.save()
    return HttpResponseRedirect('/admin/%s/edit/' % str(game.id))

# POST endpoint for changing the value of a token modifier
@login_required
def update_modifier(request, game_id, question_id):
    game = _get_game_or_404(game_id)
    question = _get_question_or_404(question_id)
    token_id = request.POST.get('token_id')
    yes_value = int(request.POST.get('yes_modifier_value'))
    no_value = int(request.POST.get('no_modifier_value'))
    
    for modifier in question.token_modifiers:
        if str(modifier.token.id) == token_id:
            modifier.yes_modifier = yes_value
            modifier.no_modifier = no_value
            break
        
    question.save()
    return HttpResponseRedirect('/admin/%s/edit/' % str(game.id))

# Endpoint for deleting an entire game
@login_required
def delete_game(request, game_id):
    game = _get_game_or_404(game_id)
    for token in game.tokens:
        token.delete()
    for question in game.questions:
        question.delete()
    game.delete()
    return HttpResponseRedirect('/admin/')

# POST endpoint for adding a question to a game
@login_required
def add_question(request, game_id):
    game = _get_game_or_404(game_id)
    question_text = request.POST.get('question_text')
    question = Question(text=question_text)
    
    for t in game.tokens:
        question.token_modifiers.append(TokenModifier(token=t, yes_modifier=0, no_modifier=0))
        
    question.save()
    game.questions.append(question)
    game.save()
    return HttpResponseRedirect('/admin/%s/edit/' % str(game.id))
    
# Endpoint for removing a question from a game
@login_required
def remove_question(request, game_id, question_id):
    game = _get_game_or_404(game_id)
    question = _get_question_or_404(question_id)
    game.questions.remove(question)
    game.save()
    question.delete()
    return HttpResponseRedirect('/admin/%s/edit/' % str(game.id))
    